from djparsing.data import BaseCssSelect


class ParserExceptions(Exception):
    default_detail = 'A parser error'
    default_field = 'system_error'
    default_obj = 'Parser'

    @staticmethod
    def _get_error(detail, field=None, obj=None):
        return '{}: {} in {}'.format(field, detail, obj)

    def __init__(self, detail=None, field=None, obj=None):
        if detail is None:
            detail = self.default_detail
        if field is None:
            field = self.default_field
        if obj is None:
            obj = self.default_obj

        self.detail = self._get_error(detail, field, obj)

    def __str__(self):
        return self.detail


class URLException(ParserExceptions):
    default_detail = 'Check attribute'
    default_obj = None
    default_field = 'url'

    @staticmethod
    def _get_error(detail, field=None, obj=None):
        return '{}: {} in {}'.format(detail, field, obj)


class FieldException(ParserExceptions):
    default_detail = 'Check the initialization '
    default_field = 'BaseCssSelect'
    default_obj = BaseCssSelect()


