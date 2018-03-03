import copy
import hashlib
import os
import logging
# from abc import ABCMeta
import shutil
from io import BytesIO
from urllib.error import URLError
from urllib.parse import urlsplit, urljoin
import lxml
import requests
from PIL import Image
from lxml.html import fromstring
# from memory_profiler import profile
from requests.exceptions import MissingSchema
from .options import Options
from .data import BaseCssSelect
from .settings import PATH_TEMP
from django.core.files.uploadedfile import InMemoryUploadedFile
# from django.core.files.uploadedfile import TemporaryUploadedFile
from django.apps import apps


def init(**kwargs):

    def dec(cls):
        if hasattr(cls, 'Meta'):
            meta = cls.Meta
            if not hasattr(meta, 'model'):
                meta.model = apps.get_model(kwargs['app'], kwargs['model'])
        else:
            setattr(cls, 'Meta', type('Meta', (), {'model': apps.get_model(kwargs['app'], kwargs['model'])}))
        return cls

    return dec


class ParserMeta(type):
    # meta class for classes parsing
    def __new__(cls, name, bases, attrs):

        parents = [base for base in bases if isinstance(base, ParserMeta)]
        if not parents:
            return super().__new__(cls, name, bases, attrs)

        new_cls = super().__new__(cls, name, bases, attrs)
        for key, attr in new_cls.__dict__.items():
            if isinstance(attr, (BaseCssSelect,)):
                attr.attr_name = key

        # we copy from the base classes fields and class Meta
        for base in reversed(parents):
            if not attrs.get('Meta', None):
                if hasattr(base, 'Meta'):
                    base_meta = copy.deepcopy(base.Meta)
                    setattr(new_cls, 'Meta', base_meta)
            for key, attr in base.__dict__.items():
                if isinstance(attr, BaseCssSelect):
                    if key not in new_cls.__dict__:
                        parent_fields = copy.deepcopy(key)
                        setattr(new_cls, parent_fields, attr)
        meta = getattr(new_cls, 'Meta', None)
        setattr(new_cls, '_opt', Options(meta))

        return new_cls


class Parser(object, metaclass=ParserMeta):
    __slots__ = ('url', 'add_field', 'block_list', 'page_url', '_opt')

    def __init__(self, url=None, **kwargs):
        self.add_field = dict()
        self.url = url
        for key, value in kwargs.items():
            setattr(self, key, value)
        for key, attr in self.__class__.__dict__.items():
            if isinstance(attr, BaseCssSelect):
                if attr.add_domain:
                    self._opt.base_domain = self._opt.get_domain(self.url)
                    self._opt.list_domain.append(key)
                if hasattr(attr, 'body'):
                    if attr.start_url:
                        self.block_list = self._set_block_html(key, attr, attr.body_count, start_url=True)
                    else:
                        self.block_list = self._set_block_html(key, attr, attr.body_count)
                    continue
                if hasattr(attr, 'img'):
                    self._opt.image = key
                self._opt.cls_attr.add(key)
        if not hasattr(self, 'block_list'):
            raise ValueError('In the {} the required "body" field'.format(self.__class__))

    def __str__(self):
        return self.__class__.__name__

    def get_block_list(self, urls, key):
        for url in urls:
            yield self._get_html(url=url).cssselect(self.__getattribute__(key))[0]

    def _set_block_html(self, key, attr, body_count, start_url=False):
        count = body_count if body_count else 30
        try:
            if start_url:
                for url in self._get_html().cssselect(attr.start_url)[0:count]:
                    if self._opt.base_domain:
                        self._opt.page_url.append('{0}{1}'.format(self._opt.base_domain, url.get("href")))
                    else:
                        self._opt.page_url.append(url.get("href"))
                return list(self.get_block_list(self._opt.page_url, key))
            return self._get_html().cssselect(self.__getattribute__(key))[0:count]
        except IndexError:
            self._get_except_val_err(attr, ind=None)
        except MissingSchema:
            self._get_except_val_err(attr, url=True, ind=None)

    def _get_except_val_err(self, attr, ind,  url=False):
        if not url:
            raise ValueError('ind: {} - Check the initialization of the {} field in {}'.format(ind, attr, self.__class__))
        raise ValueError('Check attribute url in {}'.format(self))

    def _get_html(self, url=None) -> lxml.html.HtmlElement:
        if url is None:
            response = requests.get(self.url)
        else:
            response = requests.get(url)
        return fromstring(response.text)

    @classmethod
    def set_obj(cls, url, flag):
        obj = cls(url=url)
        obj.data[flag] = True
        return obj

    @staticmethod
    def uploaded_image(url, name):
        try:
            os.chdir(PATH_TEMP)
        except FileNotFoundError:
            os.makedirs(PATH_TEMP)
            os.chdir(PATH_TEMP)
        finally:
            try:
                resp_img = requests.get(url, stream=True)
                if resp_img.status_code == 200:
                    with open(name, 'wb') as img:
                        resp_img.raw.decode_content = True
                        shutil.copyfileobj(resp_img.raw, img)
                # urlretrieve(url, name)
            except URLError:
                return None
            image = Image.open(name)
            image_io = BytesIO()
            image.save(image_io, "png", optimize=True)
            image_io.seek(0)
            os.remove(os.path.join(PATH_TEMP, name))
        return InMemoryUploadedFile(image_io, None, name, None, None, None)

    def create(self, data):
        try:
            model = self.__class__.Meta.model
        except () as e:
            raise ValueError(e)
        else:
            query = model.objects.filter(title__iexact=data['title'])
        if query.exists():
            return None
        else:
            return model.objects.create(**data)

    @staticmethod
    def is_not_word_in_field(list_1, str_1):
        for word in list_1:
            if word.lower() in str_1.lower():
                return False
        return True

    def get_element_method(self, attr_model):
        return self.__class__.__dict__[attr_model].element_method

    def _gen_pars_res(self):
        data_result = dict()
        data_result.update(self.add_field)
        for ind, block in enumerate(self.block_list):
            if hasattr(self.__class__, 'Meta') and hasattr(self.__class__.Meta, 'field_coincidence'):
                list_coincidence = getattr(self.__class__.Meta, 'coincidence')
                field = self._opt.meta.field_coincidence
                pars_field_command = 'block.cssselect(self.__getattribute__(field))[0]{}'
                try:
                    pars_res_field = eval(pars_field_command.format(self.get_element_method(field)))
                except IndexError:
                    self._get_except_val_err(field, ind=ind)
                if self.is_not_word_in_field(list_coincidence, pars_res_field):
                    continue
            command = 'block.cssselect(self.__getattribute__(attr_model))[0]{}'
            for attr_model in self._opt.cls_attr:
                obj = self.__class__.__dict__[attr_model]
                if obj.save_start_url and hasattr(obj, 'extra_data'):
                    data_result[attr_model] = self._opt.page_url[ind]
                    continue
                try:
                    pars_res = eval(command.format(self.get_element_method(attr_model)))
                except IndexError:
                    if attr_model == self._opt.image:
                        continue
                    else:
                        self._get_except_val_err(attr_model, ind)
                if attr_model in self._opt.list_domain:
                    pars_res = urljoin(self._opt.base_domain, pars_res)
                if attr_model == self._opt.image and pars_res:
                    pars_res = self.uploaded_image(
                        pars_res,
                        '{}.jpg'.format(hashlib.sha1(pars_res.encode('utf-8')).hexdigest())
                    )
                data_result[attr_model] = pars_res
            yield data_result

    def log_output(self, result):
        logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
        logging.info('{} :\n {}'.format(self, result))

    def run(self, log=False):
        for ind, res in enumerate(self._gen_pars_res()):
            if log:
                self.log_output(res)
            else:
                self.create(res)
