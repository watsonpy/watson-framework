# -*- coding: utf-8 -*-
from json import JSONEncoder
from watson.framework.views.renderers import abc


class Renderer(abc.Renderer):

    encoder = None

    def __init__(self):
        self.encoder = JSONEncoder()

    def __call__(self, view_model, context=None):
        return self.encoder.encode(view_model.data)
