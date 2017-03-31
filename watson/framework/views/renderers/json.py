# -*- coding: utf-8 -*-
from watson.common import json
from watson.framework.views.renderers import abc
from watson.framework.views.templates import shared


class Renderer(abc.Renderer):

    _encoder = None

    @property
    def encoder(self):
        if not self._encoder:
            self.encoder = json.JSONEncoder
        return self._encoder()

    @encoder.setter
    def encoder(self, encoder):
        self._encoder = encoder

    def __call__(self, view_model, context=None):
        data = view_model.data
        if view_model.template in shared.TEMPLATES.keys():
            data = self._formatted_error(view_model, context)
        return self.encoder.encode(data, **view_model.renderer_args)

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
