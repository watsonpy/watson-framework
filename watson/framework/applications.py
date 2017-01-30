# -*- coding: utf-8 -*-
import abc
from types import ModuleType
from watson.console import Runner
from watson.console.command import find_commands_in_module
from watson.common.datastructures import dict_deep_update, module_to_dict
from watson.common import imports, contextmanagers
from watson.di import ContainerAware
from watson.di.container import IocContainer
from watson.events.dispatcher import EventDispatcherAware
from watson.events.types import Event
from watson.http.messages import Request, Response
from watson.framework.exceptions import ApplicationError
from watson.framework import config as DefaultConfig, events
from watson.framework.support.console import commands as DefaultConsoleCommands


class Base(ContainerAware, EventDispatcherAware, metaclass=abc.ABCMeta):

    """The core application structure for a Watson application.

    It makes heavy use of the IocContainer and EventDispatcher classes to handle
    the wiring and executing of methods.
    The default configuration for Watson applications can be seen at watson.framework.config.

    Attributes:
        _config (dict): The configuration for the application.
        global_app (Base): A reference to the currently running application.
    """
    _config = None
    global_app = None

    @property
    def config(self):
        """Returns the configuration of the application.
        """
        return self._config

    @config.setter
    def config(self, config):
        """Sets the configuration for the application.

        Example:

        .. code-block:: python

            app = Base()
            app.config = {'some': 'settings'}

        Args:
            config (mixed): The configuration to use.
        """
        if isinstance(config, ModuleType):
            conf = module_to_dict(config, '__')
        else:
            conf = config or {}
        self._config = dict_deep_update(
            module_to_dict(DefaultConfig, '__'), conf)
        self.container.add('application.config', self.config)

    @property
    def container(self):
        """Returns the applications IocContainer.

        If no container has been created, a new container will be created
        based on the dependencies within the application configuration.
        """
        if not self._container:
            self.container = IocContainer(self.config['dependencies'])
        return self._container

    @container.setter
    def container(self, container):
        """Sets the application IocContainer.

        Adds the application to the container, which can then be accessed via
        the 'application' key.
        """
        container.add('application', self)
        self._container = container

    def __init__(self, config=None):
        """Initializes the application.

        Registers any events that are within the application configuration.

        Example:

        .. code-block:: python

            app = Base()

        Events:
            Dispatches the INIT.

        Args:
            config (mixed): See the Base.config properties.
        """
        Base.global_app = self
        self.config = config or {}
        if not self.config.get('exceptions'):
            self.exception_class = ApplicationError
        else:
            self.exception_class = imports.load_definition_from_string(
                self.config['exceptions']['class'])
        self.register_components()
        self.register_events()
        self.trigger_init_event()
        super(Base, self).__init__()

    def register_components(self):
        """Register any components specified with the application.

        Components can include the following modules:
            - dependencies
            - events
            - models
            - routes
            - views

        Registering a component will merge any configuration settings within
        the above modules prior to the application booting.

        An example component might look like:

        /component
            /views
                /index.html
            /routes.py
            /views.py
        """
        types = ('dependencies', 'events', 'routes', 'models', 'views')
        for component in self.config['components']:
            for type_ in types:
                with contextmanagers.suppress(Exception):
                    type_component = imports.load_definition_from_string(
                        '{}.{}.{}'.format(component, type_, type_))
                    if type_ == 'dependencies':
                        self.container.update(type_component)
                    if not isinstance(type_component, ModuleType):
                        self._config[type_] = dict_deep_update(
                            self._config.get(type_, {}), type_component)
            self._config['views'][
                'renderers']['jinja2']['config']['packages'].append(
                (component, 'views'))

    def trigger_init_event(self):
        """Execute any event listeners for the INIT event.
        """
        self.dispatcher.trigger(Event(events.INIT, target=self))

    def register_events(self):
        """Collect all the events from the app config and register
        them against the event dispatcher.
        """
        self.dispatcher = self.container.get('shared_event_dispatcher')
        for event, listeners in self.config['events'].items():
            for callback_priority_pair in listeners:
                try:
                    priority = callback_priority_pair[1]
                except:
                    priority = 1
                try:
                    once_only = callback_priority_pair[2]
                except:
                    once_only = False
                self.dispatcher.add(
                    event,
                    self.container.get(callback_priority_pair[0]),
                    priority,
                    once_only)

    def __call__(self, *args, **kwargs):
        return self.run(*args, **kwargs)

    @abc.abstractmethod
    def run(self):
        raise NotImplementedError('You must implement __call__')  # pragma: no cover


class Http(Base):

    """An application structure suitable for use with the WSGI protocol.

    For more information regarding creating an application consult the
    documentation.

    Example:

    .. code-block:: python

        application = applications.Http({..})
        application(environ, start_response)
    """

    def __run_inner(self, request):
        context = {
            'request': request
        }
        self.context = context
        # Retrieve the required route match for the request.
        try:
            route_result = self.dispatcher.trigger(
                Event(
                    events.ROUTE_MATCH,
                    target=self,
                    params={'context': context,
                            'router': self.container.get('router')}))
            route_match = route_result.first()
        except self.exception_class as exc:
            route_match = None
            response, view_model = self.exception(exception=exc,
                                                  context=context)
        # Execute the relevant controller for the route
        if route_match:
            try:
                dispatch_result = self.dispatcher.trigger(
                    Event(
                        events.DISPATCH_EXECUTE,
                        target=self,
                        params={'container': self.container,
                                'context': context}))
                response, view_model = dispatch_result.first()
            except self.exception_class as exc:
                response, view_model = self.exception(
                    exception=exc, context=context)
        # Render the view model or response
        if not hasattr(view_model, 'status_code'):
            try:
                self.render(context=context, view_model=view_model)
            except Exception as exc:
                response, view_model = self.exception(exception=exc,
                                                      context=context)
        # Do any cleanup required after the request has ended
        self.dispatcher.trigger(Event(events.COMPLETE,
                                      target=self,
                                      params={'container': self.container}))
        return response

    def run(self, environ, start_response):
        session = self.config['session']
        request = Request.from_environ(environ,
                                       session_class=session.get(
                                           'class', None),
                                       session_options=session.get(
                                           'options', None))
        try:
            response = self.__run_inner(request)
        except Exception as exc:
            response, view_model = self.exception(
                exception=exc, context={'request': request})
        return response(start_response)

    def exception(self, last_exception=None, **kwargs):
        event = Event(events.EXCEPTION, target=self, params=kwargs)
        result = self.dispatcher.trigger(event)
        view_model = result.first()
        response = Response(kwargs['exception'].status_code)
        context = kwargs['context']
        accept = context['request'].headers.get('accept')
        if accept:
            accept_parts = accept.split('/')
            if len(accept_parts) > 1:
                view_model.format = accept_parts[1]
        context['response'] = response
        if last_exception:
            self.render(with_dispatcher=False,
                        view_model=view_model, context=context)
        try:
            self.render(view_model=view_model, context=context)
        except Exception as exc:
            # Triggered when an exception occurs rendering the exception
            kwargs['exception'] = exc
            self.exception(last_exception=exc, **kwargs)
        return response, view_model

    def render(self, with_dispatcher=True, **kwargs):
        kwargs['container'] = self.container
        render_event = Event(events.RENDER_VIEW, target=self, params=kwargs)
        if with_dispatcher:
            self.dispatcher.trigger(render_event)
        else:
            listener = self.container.get('app_render_listener')
            listener(render_event)


class Console(Base):

    """An application structure suitable for the command line.

    For more information regarding creating an application consult the documentation.

    Example:

    .. code-block:: python

        application = applications.Console({...})
        application()
    """
    runner = None

    def __init__(self, config=None):
        super(Console, self).__init__(config)
        self.config = dict_deep_update({
            'commands': find_commands_in_module(DefaultConsoleCommands)
        }, self.config)
        self.runner = Runner(commands=self.config.get('commands'))
        self.runner.get_command = self.get_command

    def run(self, args=None):
        return self.runner(args)

    def get_command(self, command_name):
        # overrides the runners get_command method
        if command_name not in self.runner.commands:
            return None
        command = self.runner.commands[command_name]
        if not isinstance(command, str):
            self.container.add_definition(command_name, {'item': command})
        return self.container.get(command_name)
