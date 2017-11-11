import hashlib
import importlib
import os
from abc import ABCMeta, abstractclassmethod
from io import BytesIO
from urllib.error import URLError
from urllib.parse import urlsplit, urljoin
from urllib.request import urlretrieve, urlopen
import lxml
import requests
import six
from PIL import Image
from lxml.html import fromstring
from .data import BaseCssSelect
from .settings import PATH_TEMP
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files.uploadedfile import TemporaryUploadedFile
from django.apps import apps


class Parser(object):
    __slots__ = ['url', 'data', 'attributs', 'block', 'image', 'base_domain', 'list_add_domain',
                 'data_to_db', 'html']
    __metaclass__ = ABCMeta

    def __new__(cls, *args, **kwargs):
        for key, attr in cls.__dict__.items():
            if isinstance(attr, BaseCssSelect) and getattr(attr, 'body', False):
                break
        else:
            raise ValueError('In the {} the required "body" field'.format(cls))
        obj = super().__new__(cls)
        return obj

    def __init__(self, url=None, **kwargs):
        self.data_to_db = dict()
        self.base_domain = None
        self.block = str()
        self.attributs = set()
        self.list_add_domain = list()
        self.image = None
        self.url = url
        self.html = None
        for key, value in kwargs.items():
            setattr(self, key, value)

    @property
    def get_html(self) -> lxml.html.HtmlElement:
        response = requests.get(self.url)
        return fromstring(response.text)

    @staticmethod
    def uploaded_image(url, name):
        try:
            os.chdir(PATH_TEMP)
        except :
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

    def set_image(self, elem, css_path):
        try:
            url_img = elem.cssselect(css_path)[0].get("src")
        except IndexError as e:
            self.data_to_db['img'] = None
        else:
            self.data_to_db['img'] = self.uploaded_image(url_img, '{}.jpg'.format(self.data_to_db['title']))

    def create(self):
        try:
            model = apps.get_model(self.app, self.model)
        except () as e:
            raise ValueError(e)
        else:
            query = model.objects.filter(title__iexact=self.data_to_db['title'])
        if query.exists():
            return
        else:
            return model.objects.create(**self.data_to_db)

    @classmethod
    def set_obj(cls, url, flag):
        obj = cls(url=url)
        obj.data_to_db[flag] = True
        return obj

    def _get_except_val_err(self, attr):
        raise ValueError('Check the initialization of the {} field in {}'.format(attr, self.__class__))

    def __do_perform(self):
        command = 'self.block.cssselect(self.__getattribute__(attr_model))[0]{}'
        for attr_model in self.attributs:
            try:
                self.data_to_db[attr_model] = eval(command.format(self.data_to_db[attr_model]))
            except IndexError:
                if attr_model == self.image:
                    self.data_to_db[attr_model] = None
                    continue
                else:
                    self._get_except_val_err(attr_model)
            if attr_model in self.list_add_domain:
                self.data_to_db[attr_model] = urljoin(self.base_domain, self.data_to_db[attr_model])
            if attr_model == self.image and self.data_to_db[attr_model]:
                self.data_to_db[attr_model] = self.uploaded_image(
                    self.data_to_db[attr_model],
                    '{}.jpg'.format(hashlib.sha1(self.data_to_db[attr_model].encode('utf-8')).hexdigest())
                )
        return self.create()

    def run(self, url):
        self.url = url
        self.html = self.get_html
        for key, attr in self.__class__.__dict__.items():
            if isinstance(attr, BaseCssSelect):
                if getattr(attr, 'add_domain', False):
                    self.base_domain = '{0.scheme}://{0.netloc}'.format(urlsplit(self.url))
                    self.list_add_domain.append(key)
                if getattr(attr, 'body', False):
                    self._set_block_html(key, attr)
                    #### 2
                    continue
                elif getattr(attr, 'text', False):
                    self.data_to_db[key] = '.text'
                elif getattr(attr, 'text_content', False):
                    self.data_to_db[key] = '.text_content()'
                elif getattr(attr, 'attr_data', False):
                    if getattr(attr, 'img', False):
                        self.image = key
                    self.data_to_db[key] = '.get("{}")'.format(attr.attr_data)
                self.attributs.add(key)
        return self.__do_perform()

    def _set_block_html(self, key, attr):
        try:
            if getattr(attr, 'start_url', False):
                page_url = self.html.cssselect(attr.start_url)[0].get("href")
                if self.base_domain:
                    self.url = '{0}{1}'.format(self.base_domain, page_url)
                else:
                    self.url = self.page_url
                self.html = self.get_html
            self.block = self.html.cssselect(self.__getattribute__(key))[0]
        except IndexError:
            self._get_except_val_err(attr)


    # @abstractclassmethod
    # async def parsing(cls, url):
    #     pass
