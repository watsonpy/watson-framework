# -*- coding: utf-8 -*-
# Global functions for Jinja2 templates
from watson.di import ContainerAware
from watson.framework import controllers
from jinja2 import contextfunction


class Url(ContainerAware):
    """Convenience method to access the router from within a Jinja2 template.

    Example:

    .. code-block:: python

        url('route_name', keyword=arg)
    """

    __ioc_definition__ = {
        'init': {
            'router': 'router'
        }
    }

    def __init__(self, router):
        self.router = router

    def __call__(self, route_name, host=None, scheme=None, **kwargs):
        path = self.router.assemble(route_name, **kwargs)
        if host:
            path = '{0}{1}'.format(host, path)
        if scheme:
            path = '{0}://{1}'.format(scheme, path)
        return path


url = Url  # alias to Url


class Config(ContainerAware):
    """Convenience method to retrieve the configuration of the application.
    """

    __ioc_definition__ = {
        'init': {
            'application': 'application'
        }
    }

    def __init__(self, application):
        self.application = application

    def __call__(self, **kwargs):
        return self.application.config


config = Config  # alias to Config


@contextfunction
def request(context):
    """Retrieves the request from the controller.

    Deprecated: Just use 'request'

    Example:

    .. code-block:: python

        {{ request() }}
    """
    return context['context']['request']


@contextfunction
def flash_messages(context):
    """Retrieves the flash messages from the controller.

    Example:

    .. code-block:: python

        {{ flash_messages() }}
    """
    app_context = context['context']
    if 'flash_messages' not in app_context:
        if 'request' in app_context and app_context['request'].session:
            app_context['flash_messages'] = controllers.FlashMessagesContainer(
                app_context['request'].session)
        else:
            app_context['flash_messages'] = {}
    return context['context']['flash_messages']


class Translate(ContainerAware):
    __ioc_definition__ = {
        'init': {
            'translator': 'translator'
        }
    }

    def __init__(self, translator):
        self.translator = translator

    def __call__(self, string, **kwargs):
        return self.translator.translate(string, **kwargs)


_ = Translate  # alias to Translate
