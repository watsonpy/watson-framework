# -*- coding: utf-8 -*-
# TODO: Refactor these into single functions rather than classes where
# appropriate
import abc
import logging
import os
import sys
from watson.common.imports import get_qualified_name
from watson.di import ContainerAware
from watson.http import MIME_TYPES
from watson.http.messages import Response
from watson.http.sessions import session_to_cookie
from watson.framework import controllers
from watson.framework.exceptions import (NotFoundError, InternalServerError,
                                         ApplicationError)
from watson.framework.views import Model


class Base(ContainerAware, metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def __call__(self, event):
        raise NotImplementedError('You must implement __call__')  # pragma: no cover


class Route(Base):

    def __call__(self, event):
        router, request = (event.params['router'],
                           event.params['context']['request'])
        match = router.match(request)
        if match:
            event.params['context']['route_match'] = match
            return match
        raise NotFoundError(
            'Route not found for request: {0}'.format(request.url), 404)


class DispatchExecute(Base):

    def __init__(self, templates):
        self.templates = templates

    def determine_controller(self, event):
        """Figure out which controller class is associated with the route.
        """
        route_match = event.params['context']['route_match']
        try:
            controller = event.params['container'].get(
                route_match.route.options['controller'])
            controller.event = event
            return controller
        except Exception as exc:
            raise InternalServerError(
                'Controller not found for route: {0}'.format(
                    route_match.route.name)) from exc

    def get_returned_controller_data(self, controller, event):
        context = event.params['context']
        route_match = context['route_match']
        try:
            execute_params = route_match.params
            model_data = controller.execute(**execute_params)
            if isinstance(model_data, controllers.ACCEPTABLE_RETURN_TYPES):
                model_data = {'content': model_data}
            elif isinstance(model_data, Response):
                # Short circuited, skip any templating
                controller.response = context['response'] = model_data
                return model_data, model_data
            path = controller.get_execute_method_path(
                **route_match.params)
            controller_template = os.path.join(*path)
            view_template = self.templates.get(controller_template,
                                               controller_template)
            format = route_match.params.get('format', 'html')
            if isinstance(model_data, Model):
                if not model_data.template:
                    model_data.template = view_template
                else:
                    overridden_template = path[:-1] + [model_data.template]
                    model_data.template = os.path.join(
                        *overridden_template)
                if not model_data.format:
                    model_data.format = format
                view_model = model_data
            else:
                view_model = Model(
                    format=format,
                    template=view_template,
                    data=model_data)
            context['response'] = controller.response
            return controller.response, view_model
        except (ApplicationError, NotFoundError, InternalServerError) as exc:
            raise  # pragma: no cover
        except Exception as exc:
            raise InternalServerError(
                'An error occurred executing controller: {0}'.format(
                    get_qualified_name(controller))) from exc

    def add_session_cookie(self, controller):
        session_to_cookie(controller.request, controller.response)

    def __call__(self, event):
        controller = self.determine_controller(event)
        response, view_model = self.get_returned_controller_data(
            controller, event)
        self.add_session_cookie(controller)
        return response, view_model


class Exception_(Base):

    def __init__(self, handler, templates):
        self.handler = handler
        self.templates = templates

    def set_status_code(self, exception):
        try:
            exception.status_code
        except:
            setattr(exception, 'status_code', 500)
        try:
            exception.format
        except:
            setattr(exception, 'format', 'html')

    def log(self, exception):
        ignore_statuses = self.container.get(
            'application.config')['logging'].get('ignore_status', ())
        ignore_this_status = exception.status_code in ignore_statuses
        if not ignore_this_status:
            context = exception.__context__
            if not hasattr(context, '__traceback__'):
                context = exception
            logger = logging.getLogger(__name__)
            logger.error(
                str(context),
                exc_info=(context.__class__, context, context.__traceback__))

    def convert_to_view_model(self, exception, exc_data):
        str_status_code = str(exception.status_code)
        return Model(format=exception.format,
                     template=self.templates.get(
                         str_status_code,
                         self.templates[str_status_code]),
                     data=exc_data)

    def __call__(self, event):
        exception = event.params['exception']
        self.set_status_code(exception)
        self.log(exception)
        exc_data = self.handler(sys.exc_info())
        return self.convert_to_view_model(exception, exc_data)


class Render(Base):

    def __init__(self, view_config):
        self.view_config = view_config

    def __call__(self, event):
        context = event.params['context']
        response, view_model = context['response'], event.params['view_model']
        renderers = self.view_config['renderers']
        default_renderer = renderers[self.view_config['default_renderer']]
        renderer = renderers.get(
            view_model.format, default_renderer)
        try:
            mime_type = MIME_TYPES[view_model.format][0]
        except:
            if '/' in view_model.format:
                mime_type = view_model.format
            else:
                mime_type = 'text/{0}'.format(view_model.format)
        container = event.params['container']
        renderer_instance = container.get(renderer['name'])
        try:
            response.body = renderer_instance(view_model, context=context)
        except Exception as exc:
            try:
                renderer_instance = container.get(default_renderer['name'])
                view_model.format = self.view_config['default_format']
                response.body = renderer_instance(view_model, context=context)
            except Exception as exc_:
                raise InternalServerError(
                    'Template ({0}) not found'.format(
                        view_model.template)) from exc_
        if 'Content-Type' not in response.headers:
            response.headers.add('Content-Type', mime_type)
        return response
