# -*- coding: utf-8 -*-
from json import JSONEncoder
from watson.framework.views.renderers import abc


class Renderer(abc.Renderer):

    def __call__(self, view_model, context=None):
        return JSONEncoder().encode(view_model.data)
