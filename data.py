from .settings import ATTR_LIST_INIT


class BaseCSSSelect(object):
    """base class cssselect fields"""
    def __init__(self, add_domain=False, *args, **kwargs):
        self.attr_name = None
        self.add_domain = add_domain
        self.attr_data  = None

    def __set__(self, instance, value):
        value = self._check_to_field_type(instance, value)
        instance.__dict__[self.attr_name] = value

    def _get_attr_type_error(self, attr, instance=None):
        raise TypeError('attribute {} of the object {} must be a type str'.format(attr, self))

    def _check_to_field_type(self, instance, value):
        if not isinstance(value, str):
            self._get_attr_type_error(self.attr_name)
        return value


class TextCSSSelect(BaseCSSSelect):
    text = True
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class TextContentCSSSelect(BaseCSSSelect):
    text_content = True
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class BodyCSSSelect(BaseCSSSelect):
    body = True
    def __init__(self, start_url=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_url = start_url


class AttrCSSSelect(BaseCSSSelect):
    NAME_ATTRIBUTE = 'attr_data'

    def __init__(self, attr_data=None, *args, **kwargs):
        attr_data = self._check_attr_data_is_required(attr_data=attr_data, *args, **kwargs)
        super().__init__(*args, **kwargs)
        self.attr_data = attr_data

    def _check_attr_data_is_required(self, *args, **kwargs):
        """check the required attribute attr_data and type"""
        kwargs_attr = kwargs.get(self.NAME_ATTRIBUTE, False)
        if not kwargs_attr and not args:
            raise AttributeError('object {} has a required attribute {}'.format(self, self.NAME_ATTRIBUTE))
        if kwargs_attr and not isinstance(kwargs_attr, str) or args and not isinstance(args[0], str):
            self._get_attr_type_error(self.NAME_ATTRIBUTE)
        return kwargs_attr if kwargs_attr else args[0]


class ImgCSSSelect(AttrCSSSelect):
    img = True
    def __init__(self, *args, **kwargs):
        def_kwargs = self.__set_default_attr(*args, **kwargs)
        super().__init__(*args, **def_kwargs)

    def __set_default_attr(self, *args, **kwargs) -> dict:
        """Set the default attr data attribute to 'src' for the ImgCSSSelect field"""
        try:
            if self._check_attr_data_is_required(*args, **kwargs):
                return kwargs
        except AttributeError:
            kwargs.update({self.NAME_ATTRIBUTE: 'src'})
            return kwargs


def init(**kwargs):
    def dec(cls):
        try:
            for attr in ATTR_LIST_INIT:
                setattr(cls, attr, kwargs[attr])
        except() as e:
            raise AttributeError(e)
        for key, attr in cls.__dict__.items():
            if isinstance(attr, (BaseCSSSelect,)):
                attr.attr_name = key
        return cls
    return dec


