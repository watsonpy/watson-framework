# -*- coding: utf-8 -*-
from json import JSONEncoder
from watson.framework.views.renderers import abc
from watson.framework.views.templates import shared


class Renderer(abc.Renderer):

    encoder = None

    def __init__(self):
        self.encoder = JSONEncoder()

    def __call__(self, view_model, context=None):
        data = view_model.data
        if view_model.template in shared.TEMPLATES.keys():
            data = self._formatted_error(view_model, context)
        return self.encoder.encode(data)

    def _formatted_error(self, view_model, context=None):
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
