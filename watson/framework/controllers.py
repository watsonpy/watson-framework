# -*- coding: utf-8 -*-
import abc
import collections
import re
from watson.di import ContainerAware
from watson.events import types
from watson.framework import events
from watson.http.messages import Response, Request
from watson.common.imports import get_qualified_name
from watson.common.contextmanagers import suppress


ACCEPTABLE_RETURN_TYPES = (str, int, float, bool)


class Base(ContainerAware, metaclass=abc.ABCMeta):

    """The base class for all controllers.

    Attributes:
        __action__ (string): The last action that was called on the controller.
    """
    def execute(self, **kwargs):
        method = self.get_execute_method(**kwargs)
        self.__action__ = method
        return method(**kwargs) or {}

    @abc.abstractmethod
    def get_execute_method(self, **kwargs):
        raise NotImplementedError(
            'You must implement get_execute_method')  # pragma: no cover

    @abc.abstractmethod
    def get_execute_method_path(self, **kwargs):
        raise NotImplementedError(
            'You must implement get_execute_method_path')  # pragma: no cover

    def __repr__(self):
        return '<{0}>'.format(get_qualified_name(self))


class HttpMixin(object):

    """A mixin for controllers that can contain http request and response
    objects.

    Attributes:
        _request: The request made that has triggered the controller
        _response: The response that will be returned by the controller
    """
    _event = None

    @property
    def event(self):
        """The event that was triggered that caused the execution of the
        controller.

        Returns:
            watson.events.types.Event
        """
        if not self._event:
            self._event = types.Event(
                events.DISPATCH_EXECUTE, params={'context': {}})
        return self._event

    @event.setter
    def event(self, event):
        """Set the request object.

        Args:
            event (watson.events.types.Event): The triggered event.

        Raises:
            TypeError if the event type is not a subclass of
            watson.events.types.Event
        """
        if not isinstance(event, types.Event):
            raise TypeError(
                'Invalid request type, expected watson.events.types.Event')
        self._event = event

    @property
    def request(self):
        """The HTTP request relating to the controller.

        Returns:
            watson.http.messages.Request
        """
        if 'request' not in self.event.params['context']:
            return None
        return self.event.params['context']['request']

    @request.setter
    def request(self, request):
        """Set the request object.

        Args:
            request (watson.http.messages.Request): The request associated with
            the controller.

        Raises:
            TypeError if the request type is not of
            watson.http.messages.Request
        """
        if not isinstance(request, Request):
            raise TypeError(
                'Invalid request type, expected watson.http.messages.Request')
        self.event.params['context']['request'] = request

    @property
    def response(self):
        """The HTTP response related to the controller.

        If no response object has been set, then a new one will be generated.

        Returns:
            watson.http.messages.Response
        """
        if 'response' not in self.event.params['context']:
            self.response = Response()
        return self.event.params['context']['response']

    @response.setter
    def response(self, response):
        """Set the request object.

        Args:
            response (watson.http.messages.Response): The response associated
            with the controller.

        Raises:
            TypeError if the request type is not of
            watson.http.messages.Response
        """
        if not isinstance(response, Response):
            raise TypeError(
                'Invalid response type, expected watson.http.messages.Response')
        self.event.params['context']['response'] = response

    def url(self, route_name, host=None, scheme=None, **params):
        """Converts a route into a url.

        Args:
            route_name (string): The name of the route to convert
            host (string): The hostname to prepend to the route path
            scheme (string): The scheme to prepend to the route path
            params (dict): The params to use on the route

        Returns:
            The assembled url.
        """
        if not params:
            params = {}
        router = self.container.get('router')
        path = router.assemble(route_name, **params)
        if host:
            path = '{0}{1}'.format(host, path)
        if scheme:
            path = '{0}{1}'.format(scheme, path)
        return path

    def redirect(self, path, params=None, status_code=302, clear=False):
        """Redirect to a different route.

        Redirecting will bypass the rendering of the view, and the body of the
        request will be displayed.

        Also supports Post Redirect Get (http://en.wikipedia.org/wiki/Post/Redirect/Get)
        which can allow post variables to accessed from a GET resource after a
        redirect (to repopulate form fields for example).

        Args:
            path (string): The URL or route name to redirect to
            params (dict): The params to send to the route
            status_code (int): The status code to use for the redirect
            clear (bool): Whether or not the session data should be cleared

        Returns:
            A watson.http.messages.Response object.
        """
        self.response.status_code = status_code
        if self.request.is_method('POST', 'PUT'):
            self.response.status_code = status_code if status_code != 302 else 303
            self.request.session['post_redirect_get'] = dict(self.request.post)
        if clear:
            self.clear_redirect_vars()
        try:
            url = self.url(path, **params or {})
        except KeyError:
            url = path
        self.response.headers.add('location', url, replace=True)
        return self.response

    @property
    def redirect_vars(self):
        """Returns the post variables from a redirected request.
        """
        return self.request.session.get('post_redirect_get', {})

    def clear_redirect_vars(self):
        """Clears the redirected variables.
        """
        del self.request.session['post_redirect_get']

    def forward(self, controller, method=None, *args, **kwargs):
        """Fowards a request across to a different controller.

        Attributes:
            controller (string|object): The controller to execute
            method (string): The method to run, defaults to currently called method

        Returns:
            Response from other controller.
        """
        if not method:
            method = self.__action__
        if not hasattr(controller, method):
            controller = self.container.get(controller)
        controller.request = self.request
        controller.event = self.event
        return getattr(controller, method)(*args, **kwargs)

    @property
    def flash_messages(self):
        """Retrieves all the flash messages associated with the controller.

        Example:

        .. code-block:: python

            # within controller action
            self.flash_messages.add('Some message')
            return {
                'flash_messages': self.flash_messages
            }

            # within view
            {% for namespace, message in flash_messages %}
                {{ message }}
            {% endfor %}

        Returns:
            A watson.framework.controllers.FlashMessagesContainer object.
        """
        if not self.request.session:
            raise Exception('You must enable sessions in the application configuration.')
        if 'flash_messages' not in self.event.params['context']:
            self.event.params['context']['flash_messages'] = FlashMessagesContainer(
                self.request.session)
        return self.event.params['context']['flash_messages']


class FlashMessagesContainer(object):

    """Contains all the flash messages associated with a controller.

    Flash messages persist across requests until they are displayed to the user.
    """
    messages = None
    session = None
    session_key = 'flash_messages'

    def __init__(self, session):
        """Initializes the container.

        Args:
            session (watson.http.session.StorageMixin): A session object
                containing the flash messages data.
        """
        self.session = session
        if self.session_key in self.session:
            self.messages = self.session[self.session_key]
        else:
            self.clear()

    def add(self, message, namespace='info', write_to_session=True):
        """Adds a flash message within the specified namespace.

        Args:
            message (string): The message to add to the container.
            namespace (string): The namespace to sit the message in.

        Returns:
            boolean: Based on whether or not the message was added
        """
        if message in self:
            return False
        self.messages.setdefault(namespace, []).append(message)
        if write_to_session:
            # ensure that the flash messages are written to the session
            self.__write_to_session()
        return True

    def add_messages(self, messages, namespace='info'):
        """Adds a list of messages to the specified namespace.

        Args:
            messages (list|tuple): The messages to add to the container.
            namespace (string): The namespace to sit the messages in.
        """
        for message in messages:
            self.add(message, namespace, write_to_session=False)
        self.__write_to_session()

    def clear(self):
        """Clears the flash messages from the container and session.

        This is called automatically after the flash messages have been
        iterated over.
        """
        with suppress(KeyError):
            del self.session[self.session_key]
        self.messages = collections.OrderedDict()
        self.__write_to_session()

    def __write_to_session(self):
        self.session[self.session_key] = self.messages

    # Internals

    def __contains__(self, message):
        for namespace, messages in self.messages.items():
            for msg in messages:
                if msg == message:
                    return True
        return False

    def __iter__(self):
        for namespace, messages in self.messages.items():
            for message in messages:
                yield (namespace, message)
        else:
            self.clear()

    def __getitem__(self, key):
        return self.messages.get(key)

    def __len__(self):
        return len(self.messages)

    def __repr__(self):
        return '<{0} namespaces:{1}>'.format(get_qualified_name(self), len(self))


class Action(Base, HttpMixin):

    """A controller thats methods can be accessed with an _action suffix.

    Example:

    .. code-block:: python

        class MyController(controllers.Action):
            def my_func_action(self):
                return 'something'
    """
    def execute(self, **kwargs):
        actual_kwargs = kwargs.copy()
        with suppress(Exception):
            del actual_kwargs['action']
        method = self.get_execute_method(**kwargs)
        return method(**actual_kwargs) or {}

    def get_action(self, **kwargs):
        action = kwargs.get('action')
        if not action:
            action = 'index'
        return action

    def get_execute_method(self, **kwargs):
        method_name = self.get_action(**kwargs) + '_action'
        self.__action__ = method_name
        return getattr(self, method_name)

    def get_execute_method_path(self, **kwargs):
        template = re.sub('.-', '_', self.get_action(**kwargs).lower())
        return [self.__class__.__name__.lower(), template]


class Rest(Base, HttpMixin):

    """A controller thats methods can be accessed by the request method name.

    Example:

    .. code-block:: python

        class MyController(controllers.Rest):
            def GET(self):
                return 'something'
    """

    def get_execute_method(self, **kwargs):
        return getattr(self, self.request.method)

    def get_execute_method_path(self, **kwargs):
        template = self.request.method.lower()
        return [self.__class__.__name__.lower(), template]
