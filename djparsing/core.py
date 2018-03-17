import copy
# import hashlib
import os
import logging
# from abc import ABCMeta
import shutil
from io import BytesIO
from urllib.error import URLError
import lxml
import requests
from PIL import Image
from lxml.html import fromstring
# from memory_profiler import profile
from requests.exceptions import MissingSchema
from .exceptions import URLException, FieldException
from .parser import ResultParser
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
    __slots__ = ('url', 'add_field', 'block_list', 'page_url', '_opt', 'cls_attr')

    def __init__(self, url=None, **kwargs):
        self.url = url
        self.cls_attr = set()
        self.add_field = dict()
        for key, value in kwargs.items():
            setattr(self, key, value)
        for key, attr in self.__class__.__dict__.items():
            if isinstance(attr, BaseCssSelect):
                if attr.add_domain:
                    self._opt.base_domain = self._opt.get_domain(self.url)
                    self._opt.list_domain.append(key)
                if hasattr(attr, 'body'):
                    if attr.start_url:
                        self.block_list = self._get_block_html(key, attr, attr.body_count, start_url=True, **kwargs)
                    else:
                        self.block_list = self._get_block_html(key, attr, attr.body_count, **kwargs)
                    continue
                if hasattr(attr, 'img'):
                    self._opt.image = key
                self.cls_attr.add(key)
        if not hasattr(self, 'block_list'):
            raise FieldException(detail='The required field', field='BodyCssSelect', obj=self.__class__)

    def __str__(self):
        return self.__class__.__name__

    def get_page_url(self, ind):
        return self._opt.page_url[ind]

    def get_field_image(self):
        return self._opt.image

    def get_fields_add_domain(self):
        return self._opt.list_domain

    def get_base_domain(self):
        return self._opt.base_domain

    def get_field_coincidence(self):
        return self._opt.meta.field_coincidence

    def get_element_method(self, attr_model):
        return self.__class__.__dict__[attr_model].element_method

    def get_list_coincidence(self):
        return getattr(self.__class__.Meta, 'coincidence')

    def _gen_block_html(self, urls, key, **kwargs):
        for url in urls:
            yield self._get_html(url=url, **kwargs).cssselect(self.__getattribute__(key))[0]

    def _get_block_html(self, key, attr, body_count, start_url=False, **kwargs):
        count = body_count if body_count else 30
        try:
            if start_url:
                for elem_url in self._get_html(**kwargs).cssselect(attr.start_url)[0:count]:

                    if self._opt.base_domain:
                        self._opt.page_url.append('{0}{1}'.format(self._opt.base_domain, elem_url.get("href")))
                    else:
                        self._opt.page_url.append(elem_url.get("href"))
                return list(self._gen_block_html(self._opt.page_url, key, **kwargs))
            return self._get_html(**kwargs).cssselect(self.__getattribute__(key))[0:count]
        except IndexError:
            raise FieldException(field=key, obj=self)
        except MissingSchema:
            raise URLException(obj=self)

    def _get_html(self, url=None, web_driver=False, **kwargs) -> lxml.html.HtmlElement:
        if url is None:
            url = self.url
        if web_driver:
            from selenium import webdriver
            driver = webdriver.Firefox()
            driver.get(url)
            response = driver.page_source
            driver.close()
        else:
            response = requests.get(url).text
        return fromstring(response)

    # def except_val_err(self, attr, url=False, ind=None):
    #     if not url:
    #         raise ValueError(
    #             'ind: {} - Check the initialization of the {} field in {}'.format(ind, attr, self.__class__))
    #     raise ValueError('Check attribute url in {}'.format(self))

    @classmethod
    def set_obj(cls, url, flag):
        obj = cls(url=url)
        obj.add_field[flag] = True
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

    def is_field_coincidence(self):
        if hasattr(self.__class__, 'Meta') and hasattr(self.__class__.Meta, 'field_coincidence'):
            return True
        return False

    def log_output(self, result):
        logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
        logging.info('{} :\n {}'.format(self, result))

    def run(self, log=False, create=True):
        parser = ResultParser(self, self.add_field)
        if not create and not log:
            return parser
        for ind, res in enumerate(parser):
            if log:
                self.log_output(res)
            elif create:
                self.create(res)

