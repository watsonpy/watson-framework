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
def get_request(context):
    """Retrieves the request from the controller.

    Deprecated: Just use 'request'

    Example:

    .. code-block:: python

        {{ get_request() }}
    """
    return context['context']['controller'].request


@contextfunction
def get_flash_messages(context):
    """Retrieves the flash messages from the controller.

    Example:

    .. code-block:: python

        {{ get_flash_messages() }}
    """
    if 'context' not in context:
        return []
    return context['context']['controller'].flash_messages
