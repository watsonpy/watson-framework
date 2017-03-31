# -*- coding: utf-8 -*-
import abc


class Renderer(metaclass=abc.ABCMeta):
    @property
    def config(self):
        return self._config

    @config.setter
    def config(self, config):
        self._config = config

    def __init__(self, config=None):
        self.config = config or {}

    @abc.abstractmethod
    def __call__(self, view_model, context=None, **kwargs):
        raise NotImplementedError('You must implement __call__')  # pragma: no cover
