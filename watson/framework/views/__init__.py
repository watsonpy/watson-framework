# -*- coding: utf-8 -*-
from watson.common import imports


class Model(object):
    format = None
    template = None
    data = None

    def __init__(self, data=None, template=None, format=None):
        self.template = template
        self.data = {} if data is None else data
        self.format = format

    def __repr__(self):
        return (
            '<{0} template:{1} format:{2}>'.format(
                imports.get_qualified_name(self),
                self.template,
                self.format)
        )
