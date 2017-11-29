import hashlib
import os
from abc import ABCMeta
from io import BytesIO
from urllib.error import URLError
from urllib.parse import urlsplit, urljoin
from urllib.request import urlretrieve
import lxml
import requests
from PIL import Image
from lxml.html import fromstring
# from memory_profiler import profile

from .data import BaseCSSSelect
from .settings import PATH_TEMP
from django.core.files.uploadedfile import InMemoryUploadedFile
# from django.core.files.uploadedfile import TemporaryUploadedFile
from django.apps import apps


class Parser(object):
    __slots__ = ('url', 'data', 'block', 'image', 'base_domain', 'list_domain',
                 'data_to_db')
    __metaclass__ = ABCMeta

    def __new__(cls, *args, **kwargs):
        for key, attr in cls.__dict__.items():
            if isinstance(attr, BaseCSSSelect) and getattr(attr, 'body', False):
                break
        else:
            raise ValueError('In the {} the required "body" field'.format(cls))
        obj = super().__new__(cls)
        return obj

    def __init__(self, url=None, **kwargs):
        self.image = None
        self.base_domain = None
        self.data_to_db = dict()
        self.block = str()
        self.list_domain = list()
        self.url = url
        for key, value in kwargs.items():
            setattr(self, key, value)

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

    def _get_except_val_err(self, attr):
        raise ValueError('Check the initialization of the {} field in {}'.format(attr, self.__class__))

    def create(self):
        try:
            model = apps.get_model(self.app, self.model)
        except () as e:
            raise ValueError(e)
        else:
            query = model.objects.filter(title__iexact=self.data_to_db['title'])
        if query.exists():
            return None
        else:
            return model.objects.create(**self.data_to_db)

    # def set_image(self, elem, css_path):
    #     try:
    #         url_img = elem.cssselect(css_path)[0].get("src")
    #     except IndexError:
    #         self.data_to_db['img'] = None
    #     else:
    #         self.data_to_db['img'] = self.uploaded_image(url_img, '{}.jpg'.format(self.data_to_db['title']))

    def __do_perform(self, attr_pars):
        command = 'self.block.cssselect(self.__getattribute__(attr_model))[0]{}'
        for attr_model in attr_pars:
            try:
                self.data_to_db[attr_model] = eval(command.format(self.data_to_db[attr_model]))
            except IndexError:
                if attr_model == self.image:
                    self.data_to_db[attr_model] = None
                    continue
                else:
                    self._get_except_val_err(attr_model)
            if attr_model in self.list_domain:
                self.data_to_db[attr_model] = urljoin(self.base_domain, self.data_to_db[attr_model])
            if attr_model == self.image and self.data_to_db[attr_model]:
                self.data_to_db[attr_model] = self.uploaded_image(
                    self.data_to_db[attr_model],
                    '{}.jpg'.format(hashlib.sha1(self.data_to_db[attr_model].encode('utf-8')).hexdigest())
                )
        print(self.data_to_db)
        return self.create()

    def _check_attr(self, html):
        attributs = set()
        for key, attr in self.__class__.__dict__.items():
            if isinstance(attr, BaseCSSSelect):
                if attr.add_domain is not None:
                    self.base_domain = self.get_domain(self.url)
                    self.list_domain.append(key)
                if hasattr(attr, 'body'):
                    self._set_block_html(key, attr, html)
                    continue
                if hasattr(attr, 'img'):
                    self.image = key
                self.data_to_db[key] = attr.element_method
                attributs.add(key)
        return attributs

    def run(self, **kwargs):
        if not self.url:
            try:
                self.url = kwargs['url']
            except KeyError:
                raise ValueError('not attribute url')
        attr_to_pars = self._check_attr(self.get_html)
        return self.__do_perform(attr_to_pars)

    def _set_block_html(self, key, attr, html):
        try:
            if getattr(attr, 'start_url', False):
                page_url = html.cssselect(attr.start_url)[0].get("href")
                if self.base_domain:
                    self.url = '{0}{1}'.format(self.base_domain, page_url)
                else:
                    self.url = page_url
                html = self.get_html
            self.block = html.cssselect(self.__getattribute__(key))[0]
        except IndexError:
            self._get_except_val_err(attr)



########################################################################################################
            # @abstractclassmethod
            # async def parsing(cls, url):
            #     pass
