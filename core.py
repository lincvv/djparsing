import copy
import hashlib
import os
# from abc import ABCMeta
from io import BytesIO
from urllib.error import URLError
from urllib.parse import urlsplit, urljoin
from urllib.request import urlretrieve
import lxml
import requests
from PIL import Image
from lxml.html import fromstring
# from memory_profiler import profile
from requests.exceptions import MissingSchema
from .data import BaseCSSSelect
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

    def __new__(cls, name, bases, attrs):

        parents = [base for base in bases if isinstance(base, ParserMeta)]
        if not parents:
            return super().__new__(cls, name, bases, attrs)

        new_cls = super().__new__(cls, name, bases, attrs)
        for key, attr in new_cls.__dict__.items():
            if isinstance(attr, (BaseCSSSelect,)):
                attr.attr_name = key

        for base in reversed(parents):
            if not attrs.get('Meta', None):
                if hasattr(base, 'Meta'):
                    base_meta = copy.deepcopy(base.Meta)
                    setattr(new_cls, 'Meta', base_meta)
            for key, attr in base.__dict__.items():
                if isinstance(attr, BaseCSSSelect):
                    if key not in new_cls.__dict__:
                        parent_fields = copy.deepcopy(key)
                        setattr(new_cls, parent_fields, attr)

        return new_cls


class Parser(object, metaclass=ParserMeta):
    __slots__ = ('url', 'data', 'block', 'image', 'base_domain', 'list_domain',
                 'data_to_db', 'attrib',)

    def __init__(self, url=None, **kwargs):
        self.data_to_db = dict()
        self.list_domain = list()
        self.url = url
        self.attrib = set()
        self.image = None
        for key, value in kwargs.items():
            setattr(self, key, value)
        for key, attr in self.__class__.__dict__.items():
            if isinstance(attr, BaseCSSSelect):
                if attr.add_domain:
                    self.base_domain = self.get_domain(self.url)
                    self.list_domain.append(key)
                if hasattr(attr, 'body'):
                    self.block = self._set_block_html(key, attr)
                    continue
                if hasattr(attr, 'img'):
                    self.image = key
                self.attrib.add(key)
        if not hasattr(self, 'block'):
            raise ValueError('In the {} the required "body" field'.format(self.__class__))

    def _set_block_html(self, key, attr):
        try:
            if getattr(attr, 'start_url', False):
                page_url = self.get_html.cssselect(attr.start_url)[0].get("href")
                if self.base_domain:
                    self.url = '{0}{1}'.format(self.base_domain, page_url)
                else:
                    self.url = page_url
            return self.get_html.cssselect(self.__getattribute__(key))[0]
        except IndexError:
            self._get_except_val_err(attr)
        except MissingSchema:
            self._get_except_val_err(attr, url=False)

    def _get_except_val_err(self, attr, url=True):
        if url:
            raise ValueError('Check the initialization of the {} field in {}'.format(attr, self.__class__))
        raise ValueError('Check attribute url in {}'.format(self))

    @property
    def get_html(self) -> lxml.html.HtmlElement:
        response = requests.get(self.url)
        return fromstring(response.text)

    @staticmethod
    def get_domain(url):
        return '{0.scheme}://{0.netloc}'.format(urlsplit(url))

    @classmethod
    def set_obj(cls, url, flag):
        obj = cls(url=url)
        obj.data_to_db[flag] = True
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
                urlretrieve(url, name)
            except URLError:
                return None
            image = Image.open(name)
            image_io = BytesIO()
            image.save(image_io, "png", optimize=True)
            image_io.seek(0)
            os.remove(os.path.join(PATH_TEMP, name))
        return InMemoryUploadedFile(image_io, None, name, None, None, None)

    def create(self):
        try:
            model = self.__class__.Meta.model
        except () as e:
            raise ValueError(e)
        else:
            query = model.objects.filter(title__iexact=self.data_to_db['title'])
        if query.exists():
            return None
        else:
            return model.objects.create(**self.data_to_db)

    @staticmethod
    def is_not_word_in_field(list_1, str_1):
        for word in list_1:
            if word.lower() in str_1.lower():
                return False
        return True

    def get_element_method(self, attr_model):
        return self.__class__.__dict__[attr_model].element_method

    def _get_pars_fiaeld(self):
        field = self.__class__.Meta.field_coincidence
        pars_field = 'self.block.cssselect(self.__getattribute__(field))[0]{}'
        try:
            return eval(pars_field.format(self.get_element_method(field)))
        except IndexError:
            self._get_except_val_err(field)

    def gen_pars_res(self):

        if hasattr(self.__class__, 'Meta') and hasattr(self.__class__.Meta, 'field_coincidence'):
            list_coincidence = getattr(self.__class__.Meta, 'coincidence')
            pars_res_field = self._get_pars_fiaeld()
            if self.is_not_word_in_field(list_coincidence, pars_res_field):
                self.data_to_db = None
                return
        command = 'self.block.cssselect(self.__getattribute__(attr_model))[0]{}'
        for attr_model in self.attrib:
            try:
                pars_res = eval(command.format(self.get_element_method(attr_model)))
            except IndexError:
                if attr_model == self.image:
                    pars_res = None
                    continue
                else:
                    self._get_except_val_err(attr_model)
            if attr_model in self.list_domain:
                pars_res = urljoin(self.base_domain, pars_res)
            if attr_model == self.image and pars_res:
                pars_res = self.uploaded_image(
                    pars_res,
                    '{}.jpg'.format(hashlib.sha1(pars_res.encode('utf-8')).hexdigest())
                )
            self.data_to_db[attr_model] = pars_res
            yield pars_res

    def run(self):
        for res in self.gen_pars_res():
            # print(res)
            pass
        if self.data_to_db is None:
            return None
        return self.create()

