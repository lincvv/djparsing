

class BaseCssSelect(object):
    """base class cssselect fields"""
    element_method = None
    extra_data = False
    attr = False
    text = False
    text_content = False

    def __init__(self, add_domain=False, save_start_url=False, save_url=False, many=False, *args, **kwargs):
        self.add_domain = add_domain
        self.save_start_url = save_start_url
        self.save_url = save_url
        self.many = many
        self.attr_name = None
        self.attr_data = None

    def __set__(self, instance, value):
        value = self._check_to_field_type(instance, value)
        instance.__dict__[self.attr_name] = value

    def _except_attr_type_error(self, attr, instance=None):
        raise TypeError('attribute {} of the object {} must be a type str in {}'.format(attr, self, instance))

    def _check_to_field_type(self, instance, value):
        if not isinstance(value, str):
            self._except_attr_type_error(self.attr_name, instance)
        return value


class ExtraDataField(BaseCssSelect):
    extra_data = True


class TextCssSelect(BaseCssSelect):
    element_method = '.text'
    text =True


class TextContentCssSelect(BaseCssSelect):
    element_method = '.text_content()'
    text_content = True


class BodyCssSelect(BaseCssSelect):
    body = True

    def __init__(self, start_url=None, body_count=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_url = start_url
        self.body_count = body_count


class AttrCssSelect(BaseCssSelect):
    attr = True
    NAME_ATTRIBUTE = 'attr_data'
    element_method = '.get("{}")'

    def __init__(self, attr_data=None, *args, **kwargs):
        attr_data = self._check_attr_data_is_required(attr_data=attr_data, *args, **kwargs)
        super().__init__(*args, **kwargs)
        self.attr_data = attr_data
        self.element_method = self.element_method.format(attr_data)

    def _check_attr_data_is_required(self, *args, **kwargs):
        """check the required attribute attr_data and type"""
        kwargs_attr = kwargs.get(self.NAME_ATTRIBUTE, False)
        if not kwargs_attr and not args:
            raise AttributeError('object {} has a required attribute {}'.format(self, self.NAME_ATTRIBUTE))
        if kwargs_attr and not isinstance(kwargs_attr, str) or args and not isinstance(args[0], str):
            self._except_attr_type_error(self.NAME_ATTRIBUTE)
        return kwargs_attr if kwargs_attr else args[0]


class ImgCssSelect(AttrCssSelect):
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



