import hashlib
from urllib.parse import urljoin

from .exceptions import FieldException


class ResultParser(object):
    def __init__(self, obj_parser):
        self.obj_parser = obj_parser

    def __repr__(self):
        return 'ResultParser({})'.format(self.obj_parser)

    def get_object_field(self, field_name):
        return self.obj_parser.__class__.__dict__[field_name]

    def get_elem_result(self, block, obj_field):
        elem = block.cssselect(self.obj_parser.__getattribute__(obj_field.attr_name))[0]
        if obj_field.text:
            return elem.text
        elif obj_field.text_content:
            return elem.text_content()
        elif obj_field.attr:
            return elem.get(obj_field.attr_data)

    def get_field(self, block):
        field = self.obj_parser.get_field_coincidence()
        obj = self.get_object_field(field)
        try:
            res_field = self.get_elem_result(block=block, obj_field=obj)
        except IndexError:
            raise FieldException(field=field, obj=obj)
        else:
            return res_field

    def is_word_in_field(self, field):
        list_coincidence = self.obj_parser.get_list_coincidence()
        for word in list_coincidence:
            if word.lower() in field.lower():
                return True
        return False

    def __iter__(self):
        for ind, block in enumerate(self.obj_parser.block_list):
            yield ind
            if self.obj_parser.is_field_coincidence():
                field_result = self.get_field(block)
                if not self.is_word_in_field(field=field_result):
                    continue
            for attr_name in self.obj_parser.cls_attr:
                obj = self.get_object_field(attr_name)
                if obj.save_start_url and hasattr(obj, 'extra_data'):
                    try:
                        yield {attr_name: self.obj_parser.get_page_url(ind=ind)}
                    except IndexError:
                        raise ValueError('Check the field with the attribute "start_url"')
                    continue
                if obj.save_url:
                    yield {attr_name: self.obj_parser.url}
                    continue
                if obj.many:
                    data_input = list()
                    for data in block.cssselect(self.obj_parser.__getattribute__(attr_name)):
                        if obj.attr:
                            data_input.append(data.get(obj.attr_data))
                        if obj.text:
                            data_input.append(data.text)
                    yield {attr_name: data_input}
                    continue
                try:
                    pars_result = self.get_elem_result(block=block, obj_field=obj)
                except IndexError:
                    if attr_name == self.obj_parser.get_field_image():
                        continue
                    else:
                        raise FieldException(field=attr_name, obj=self.obj_parser)
                if attr_name in self.obj_parser.get_fields_add_domain():
                    pars_result = urljoin(self.obj_parser.get_base_domain(), pars_result)
                if attr_name == self.obj_parser.get_field_image() and pars_result:
                    pars_result = self.obj_parser.uploaded_image(
                        pars_result,
                        '{}.jpg'.format(hashlib.sha1(pars_result.encode('utf-8')).hexdigest())
                    )
                yield {attr_name: pars_result}

