# -*- coding: utf-8 -*-
import abc
from watson.common import strings


class Panel(metaclass=abc.ABCMeta):
    data = None
    title = 'Unnamed Panel'
    icon = 'ellipsis-v'
    event = None

    def __init__(self, config, renderer, application):
        self.config = config
        self.renderer = renderer
        self.application = application
        self.application_run = application.run
        self.data = {}

    @property
    def _template(self):
        return 'debug/panels/{}'.format(strings.url_safe(self.title.lower()))

    def _render(self, data):
        return self.renderer.render(self._template, data)

    def register_listeners(self):
        pass

    @abc.abstractmethod
    def render(self):
        raise NotImplementedError('You must implement render for this panel')

    @abc.abstractmethod
    def render_key_stat(self):
        raise NotImplementedError('You must implement render for this panel')

    def __str__(self):
        return self.render()
