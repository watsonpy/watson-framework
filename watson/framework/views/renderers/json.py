# -*- coding: utf-8 -*-
from json import JSONEncoder
from watson.framework.views.renderers import abc
from watson.common import contextmanagers


class Renderer(abc.Renderer):

    def __call__(self, view_model):
        with contextmanagers.ignored(KeyError, TypeError):
            del view_model.data['context']
        return JSONEncoder().encode(view_model.data)
