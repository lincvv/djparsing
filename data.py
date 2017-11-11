from .settings import ATTR_LIST_INIT


class BaseCssSelect(object):
    """base class cssselect fields"""
    def __init__(self, add_domain=False, *args, **kwargs):
        self.attr_name = None
        self.add_domain = add_domain

    def __set__(self, instance, value):
        value = self._check_to_field_type(instance, value)
        instance.__dict__[self.attr_name] = value

    def _get_attr_type_error(self, attr, instance=None):
        raise TypeError('attribute {} of the object {} must be a type str'.format(attr, self))

    def _check_to_field_type(self, instance, value):
        if not isinstance(value, str):
            self._get_attr_type_error(self.attr_name)
        return value


class TextCssSelect(BaseCssSelect):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text = True


class TextContentCssSelect(BaseCssSelect):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text_content = True


class BodyCSSSelect(BaseCssSelect):
    def __init__(self, start_url=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_url = start_url
        self.body = True


class AttrCSSSelect(BaseCssSelect):
    VALID_ATTRIBUTE = 'attr_data'

    def __init__(self, attr_data=None, *args, **kwargs):
        # print(self.__class__, '->', self.__class__.__bases__[0])
        try:
            attr_data = self._check_attr_data_is_required(attr_data=attr_data, *args, **kwargs)
        except ():
            pass
        else:
            super().__init__(*args, **kwargs)
            self.attr_data = attr_data

    def _check_attr_data_is_required(self, *args, **kwargs):
        """check the required attribute attr_data and type"""
        kwargs_attr = kwargs.get(self.VALID_ATTRIBUTE, False)
        if not kwargs_attr and not args:
            raise AttributeError('object {} has a required attribute {}'.format(self, self.VALID_ATTRIBUTE))
        if kwargs_attr and not isinstance(kwargs_attr, str) or args and not isinstance(args[0], str):
            self._get_attr_type_error(self.VALID_ATTRIBUTE)
        # if args and not isinstance(args[0], str):
        #     self.attr_error()
        return kwargs_attr if kwargs_attr else args[0]


class ImgCSSSelect(AttrCSSSelect):
    def __init__(self, *args, **kwargs):
        def_kwargs = self.__set_default_attr(*args, **kwargs)
        super().__init__(*args, **def_kwargs)
        self.img = True

    def __set_default_attr(self, *args, **kwargs) -> dict:
        """Set the default attr data attribute to 'src' for the ImgCSSSelect field"""
        try:
            if self._check_attr_data_is_required(*args, **kwargs):
                return kwargs
        except AttributeError:
            kwargs.update({self.VALID_ATTRIBUTE: 'src'})
            return kwargs

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
            if isinstance(attr, (BaseCssSelect,)):
                attr.attr_name = key
        return cls
    return dec


