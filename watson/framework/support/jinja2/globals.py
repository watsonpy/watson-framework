# -*- coding: utf-8 -*-
# Global functions for Jinja2 templates
from watson.di import ContainerAware
from jinja2 import contextfunction


class Url(ContainerAware):
    """Convenience method to access the router from within a Jinja2 template.

    Example:

    .. code-block:: python

        url('route_name', keyword=arg)
    """
    def __call__(self, route_name, host=None, scheme=None, **kwargs):
        path = self.container.get('router').assemble(route_name, **kwargs)
        if host:
            path = '{0}{1}'.format(host, path)
        if scheme:
            path = '{0}{1}'.format(scheme, path)
        return path


url = Url  # alias to Url


class Config(ContainerAware):
    """Convenience method to retrieve the configuration of the application.
    """
    def __call__(self, **kwargs):
        return self.container.get('application').config


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
    if 'flash_messages' not in context['context']:
        return {}
    return context['context']['flash_messages']
