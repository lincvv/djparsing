import os

from .settings import ATTR_LIST_INIT


class Base(object):
    def __init__(self, attr_data=None, body=None, text=None, text_content=None, start_url=None,
                 img=None):
        self.img = img
        self.start_url = start_url
        self.attr_data = attr_data
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


class BodyCSSSelect(Base):
    def __init__(self, *args, **kwargs):
        super().__init__(body=True, *args, **kwargs)

class AttrCSSSelect(Base):
    VALID_ATTRIBUTE = 'attr_data'
    def __init__(self, *args, **kwargs): 
        self.validate_attr(*args, **kwargs)
        super().__init__(*args, **kwargs)


    def validate_attr(self, *args, **kwargs):
        try:
            if  not (args or kwargs[self.VALID_ATTRIBUTE]):
                pass
        except KeyError:
            raise AttributeError('instance {} имеет обязательный атрибут {}'.format(self, self.VALID_ATTRIBUTE))

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
            if isinstance(attr, (Base,)):
                attr.attr_name = key
        return cls
    return dec


