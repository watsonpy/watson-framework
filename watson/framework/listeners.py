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
from watson.framework import controllers
from watson.framework.exceptions import NotFoundError, InternalServerError, ExceptionHandler, ApplicationError
from watson.framework.views import Model


class Base(ContainerAware, metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def __call__(self, event):
        raise NotImplementedError('You must implement __call__')  # pragma: no cover


class Route(Base):

    def __call__(self, event):
        router, request = event.params['router'], event.params['request']
        matches = router.matches(request)
        if not matches:
            raise NotFoundError(
                'Route not found for request: {0}'.format(request.url),
                404)
        event.params['route_match'] = matches[0]
        return matches[0]


class DispatchExecute(Base):

    def __init__(self, templates):
        self.templates = templates

    def __call__(self, event):
        route_match = event.params['route_match']
        try:
            controller_class = route_match.route.options['controller']
            container = event.params['container']
            if controller_class not in container.config['definitions']:
                container.add(controller_class, controller_class, 'prototype')
            else:
                controller_definition = container.config[
                    'definitions'][controller_class]
                controller_definition['type'] = 'prototype'
                if 'item' not in controller_definition:
                    controller_definition['item'] = controller_class

            controller = event.params['container'].get(controller_class)
        except Exception as exc:
            raise InternalServerError(
                'Controller not found for route: {0}'.format(
                    route_match.route.name)) from exc
        event.params['controller_class'] = controller
        controller.event = event
        controller.request = event.params['request']
        try:
            execute_params = route_match.params
            model_data = controller.execute(**execute_params)
            if model_data is None:
                raise InternalServerError(
                    'The controller {0} did not return any data.'.format(controller))
            short_circuit = False
            if isinstance(model_data, controllers.ACCEPTABLE_RETURN_TYPES):
                model_data = {'content': model_data}
            elif isinstance(model_data, Response):
                short_circuit = True
                response = model_data
            if not short_circuit:
                context = {'context': {'controller': controller}}
                path = controller.get_execute_method_path(
                    **route_match.params)
                controller_template = os.path.join(*path)
                view_template = self.templates.get(controller_template,
                                                   controller_template)
                format = route_match.params.get('format', 'html')
                if isinstance(model_data, Model):
                    if isinstance(model_data.data, dict):
                        model_data.data.update(context)
                    if not model_data.template:
                        model_data.template = view_template
                    else:
                        overridden_template = path[:-1] + [model_data.template]
                        model_data.template = os.path.join(
                            *overridden_template)
                    if not model_data.format:
                        model_data.format = format
                    response = model_data
                else:
                    if isinstance(model_data, dict):
                        model_data.update(context)
                    response = Model(
                        format=format,
                        template=view_template,
                        data=model_data)
        except (ApplicationError, NotFoundError, InternalServerError) as exc:
            raise
        except Exception as exc:
            raise InternalServerError(
                'An error occurred executing controller: {0}'.format(get_qualified_name(controller))) from exc
        controller.request.session_to_cookie()
        if controller.request.cookies.modified:
            controller.response.cookies.merge(controller.request.cookies)
        return response


class Exception_(Base):

    def __init__(self, handler, templates):
        self.handler = handler
        self.templates = templates

    def __call__(self, event):
        exception = event.params['exception']
        try:
            status_code = exception.status_code
        except:
            status_code = 500
            setattr(exception, 'status_code', status_code)
        exc_data = self.handler(sys.exc_info(), event.params)
        ignore_statuses = self.container.get(
            'application.config')['logging'].get('ignore_status', {})
        ignore_this_status = ignore_statuses.get(str(status_code), False)
        if not ignore_this_status:
            context = exception.__context__
            if not hasattr(context, '__traceback__'):
                context = exception
            logger = logging.getLogger(__name__)
            logger.error(
                str(context),
                exc_info=(context.__class__, context, context.__traceback__))
        return Model(format='html',  # should this take the format from the request?
                     template=self.templates.get(
                         str(status_code),
                         self.templates[str(status_code)]),
                     data=exc_data)


class Render(Base):

    def __init__(self, view_config):
        self.view_config = view_config

    def __call__(self, event):
        response, view_model = event.params[
            'response'], event.params['view_model']
        renderers = self.view_config['renderers']
        renderer = renderers.get(view_model.format, renderers['default'])
        try:
            mime_type = MIME_TYPES[view_model.format][0]
        except:
            if '/' in view_model.format:
                mime_type = view_model.format
            else:
                mime_type = 'text/{0}'.format(view_model.format)
        renderer_instance = event.params['container'].get(renderer['name'])
        renderer_instance.response = response
        renderer_instance.request = event.params['request']
        try:
            response.body = renderer_instance(view_model)
            if 'Content-Type' not in response.headers:
                response.headers.add('Content-Type', mime_type)
        except Exception as exc:
            raise InternalServerError(
                'Template ({0}) not found'.format(
                    view_model.template)) from exc
