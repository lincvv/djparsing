import hashlib
import importlib
import os
from abc import ABCMeta, abstractclassmethod
from io import BytesIO
from urllib.parse import urlsplit
from urllib.request import urlretrieve, urlopen
import lxml
import requests
import six
from PIL import Image
from lxml.html import fromstring
from .data import Base
from .settings import PATH_TEMP
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files.uploadedfile import TemporaryUploadedFile
from django.apps import apps


class Parser(object):
    __slots__ = ['url', 'data', 'attributs', 'block', 'image', 'page_url']
    __metaclass__ = ABCMeta

    def __new__(cls, *args, **kwargs):
        for key, attr in cls.__dict__.items():
            if isinstance(attr, Base) and attr.__dict__['body']:
                break
        else:
            raise ValueError('В класе: {} должно быть поле с атрибутом body'.format(cls))
        obj = super().__new__(cls)
        obj.data = {}
        return obj

    def __init__(self, url=None, **kwargs):
        self.image = None
        self.block = str()
        self.page_url = str()
        self.attributs = set()
        self.url = url
        for key, value in six.iteritems(kwargs):
            setattr(self, key, value)

    def get_html(self) -> lxml.html.HtmlElement:
        response = requests.get(self.url)
        return fromstring(response.text)

    @staticmethod
    def uploaded_image(url, name):
        try:
            os.chdir(PATH_TEMP)
        except:
            os.makedirs(PATH_TEMP)
        finally:
            urlretrieve(url, name)
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
            self.data['img'] = None
        else:
            self.data['img'] = self.uploaded_image(url_img, '{}.jpg'.format(self.data['title']))

    def create(self):
        try:
            model = apps.get_model(self.app, self.model)
        except () as e:
            raise ValueError(e)
        else:
            query = model.objects.filter(title__iexact=self.data['title'])
        if query.exists():
            return
        else:
            return model.objects.create(**self.data)

    @classmethod
    def set_obj(cls, url, flag):
        obj = cls(url=url)
        obj.data[flag] = True
        return obj

    def __do_perform(self):
        command = 'self.block.cssselect(self.__getattribute__(attr))[0]{}'
        for attr in self.attributs:
            try:
                self.data[attr] = eval(command.format(self.data[attr]))
            except IndexError as e:
                if attr == self.image:
                    self.data[attr] = None
                    continue
                else:
                    raise ValueError('Проверьте правильность инициализации поля {} класа {}'.format(attr, self.__class__))
            if attr == self.image and self.data[attr]:
                self.data[attr] = self.uploaded_image(
                    self.data[attr],
                    '{}.jpg'.format(hashlib.sha1(self.data[attr].encode('utf-8')).hexdigest())
                )
        return self.create()

    def run(self, url):
        self.url = url
        html = self.get_html()
        for key, attr in self.__class__.__dict__.items():
            if isinstance(attr, Base):
                if attr.body:
                    if attr.start_url:
                        self.page_url = html.cssselect(attr.start_url)[0].get("href")
                        self.url = '{0.scheme}://{0.netloc}{1}'.format(urlsplit(self.url), self.page_url)
                        html = self.get_html()
                    self.block = html.cssselect(self.__getattribute__(key))[0]
                    continue
                elif attr.text:
                    self.data[key] = '.text'
                elif attr.text_content:
                    self.data[key] = '.text_content()'
                elif attr.attr_data:
                    if attr.img:
                        self.image = key
                    self.data[key] = '.get("{}")'.format(attr.attr_data)
                self.attributs.add(key)
        return self.__do_perform()

    # @abstractclassmethod
    # async def parsing(cls, url):
    #     pass
