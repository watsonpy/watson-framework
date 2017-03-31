# -*- coding: utf-8 -*-
from watson.framework.views.renderers import abc
from watson.common import xml
from watson.framework.views.templates import shared


class Renderer(abc.Renderer):

    def __call__(self, view_model, context=None):
        data = view_model.data
        if view_model.template in shared.TEMPLATES.keys():
            data = self._formatted_error(view_model, context)
        _xml = xml.from_dict(data)
        return xml.to_string(_xml, xml_declaration=True)

    def _formatted_error(self, view_model, context=None, **kwargs):
        if not view_model.data['debug']:
            if context and context.get('response'):
                status_code = context['response'].status_code
            else:
                status_code = -1
            try:
                data = shared.TEMPLATES[view_model.template]
            except:
                data = {
                    'name': 'Unknown Error',
                    'message': 'An unknown {} error has occurred.'.format(
                        status_code)
                }
        else:
            data = view_model.data
        return data
