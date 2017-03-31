# -*- coding: utf-8 -*-
from watson.common import imports


class Model(object):
    format = None
    template = None
    data = None
    renderer_args = None

    def __init__(
            self, data=None, template=None, format=None, renderer_args=None):
        self.template = template
        self.data = data if data else data
        self.format = format
        self.renderer_args = renderer_args if renderer_args else {}

    def __repr__(self):
        return (
            '<{0} template:{1} format:{2}>'.format(
                imports.get_qualified_name(self),
                self.template,
                self.format)
        )
