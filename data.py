import os

from home.parser.settings import ATTR_LIST_INIT


class Xpath(object):
    def __init__(self, body=None, text=None, text_content=None, data=None, href=None,
                 img=None):
        self.img = img
        self.href = href
        self.data = data
        self.text_content = text_content
        self.text = text
        self.body = body
        self.attr_name = None

    def __set__(self, instance, value):
        value = self.validate(instance, value)
        instance.__dict__[self.attr_name] = value

    def validate(self, instance, value):
        if not isinstance(value, str) and isinstance(self, self.__class__):
            raise ValueError('атрибут  {} может иметь только тип str'.format(self.attr_name))
        return value


# class XpathValidated(abc.ABC, XpathBase):
#     def __set__(self, instance, value):
#         value = self.validate(instance, value)
#         super().__set__(instance, value)
#
#     @abc.abstractmethod
#     def validate(self, instance, value):
#         pass


def init(**kwargs):
    def dec(cls):
        try:
            for attr in ATTR_LIST_INIT:
                setattr(cls, attr, kwargs[attr])
        except() as e:
            raise AttributeError(e)
        for key, attr in cls.__dict__.items():
            if isinstance(attr, (Xpath, )):
                attr.attr_name = key
        return cls
    return dec


