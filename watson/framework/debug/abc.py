# -*- coding: utf-8 -*-
import abc


class Panel(metaclass=abc.ABCMeta):
    data = None
    title = 'Unnamed Panel'
    event = None

    def __init__(self, config, renderer, application):
        self.config = config
        self.renderer = renderer
        self.application = application
        self.application_run = application.run
        self.data = {}

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
