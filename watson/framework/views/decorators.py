# -*- coding: utf-8 -*-
from watson.framework import views, controllers


def view(template=None, format=None):
    """Return the view model in a specific format and with a specific template.

    This will not work if the response returned from the controller is of
    the watson.http.messages.Response type.

    Args:
        func (callable): the function that is being wrapped
        template (string): the template to use
        format (string): the format to output as

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
            controller_response = func(self, *args, **kwargs)
            if controller_response is None:
                controller_response = {}
            if isinstance(controller_response, controllers.ACCEPTABLE_RETURN_TYPES):
                controller_response = {'content': controller_response}
            if isinstance(controller_response, (dict, list, tuple)):
                controller_response = views.Model(data=controller_response)
            if format:
                controller_response.format = format
            if template:
                controller_response.template = template
            return controller_response
        return wrapper
    return decorator
