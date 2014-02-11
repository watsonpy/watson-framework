# -*- coding: utf-8 -*-
from watson.framework.views.renderers import abc
from watson.common import xml


class Renderer(abc.Renderer):

    def __call__(self, view_model, context=None):
        _xml = xml.from_dict(view_model.data)
        return xml.to_string(_xml, xml_declaration=True)
