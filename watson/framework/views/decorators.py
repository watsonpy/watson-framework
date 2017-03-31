# -*- coding: utf-8 -*-
from watson.framework import views, controllers
from watson.http import messages


def view(template=None, format=None, renderer_args=None):
    """Return the view model in a specific format and with a specific template.

    This will not work if the response returned from the controller is of
    the watson.http.messages.Response type.

    Args:
        func (callable): the function that is being wrapped
        template (string): the template to use
        format (string): the format to output as
        renderer_args (mixed): args to be passed to the renderer

    Returns:
        The view model in the specific format

    Example:

    .. code-block:: python

        class MyClass(controllers.Rest):
            @view(template='edit')
            def create_action(self):
                return 'something'
    """
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            response = func(self, *args, **kwargs)
            if response is None:
                response = {}
            elif isinstance(response, controllers.ACCEPTABLE_RETURN_TYPES):
                response = {'content': response}
            if not isinstance(response, messages.Response):
                response = views.Model(data=response)
            if isinstance(response, views.Model):
                if format:
                    response.format = format
                if template:
                    response.template = template
                if renderer_args:
                    response.renderer_args = renderer_args
            return response
        return wrapper
    return decorator
