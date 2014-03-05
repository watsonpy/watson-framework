# -*- coding: utf-8 -*-
from wsgiref import util
from pytest import raises
from watson.di.container import IocContainer
from watson.events.types import Event
from watson.http.messages import Request, Response
from watson.routing.routers import DictRouter
from watson.routing.routes import RouteMatch, LiteralRoute
from watson.framework.exceptions import NotFoundError, InternalServerError
from watson.framework import listeners, config, views, applications
from tests.watson.framework.support import sample_environ


class TestBaseListener(object):

    def test_missing_call(self):
        with raises(TypeError):
            listeners.Base()


class TestRouteListener(object):

    def create_event(self, **kwargs):
        router = DictRouter({'home': {'path': '/'}})
        environ = {}
        util.setup_testing_defaults(environ)
        environ.update(**kwargs)
        context = {'request': Request.from_environ(environ)}
        event = Event(
            'TestEvent',
            params={'router': router,
                    'context': context})
        return event

    def test_response(self):
        listener = listeners.Route()
        result = listener(self.create_event())
        assert isinstance(result, RouteMatch)

    def test_not_found(self):
        with raises(NotFoundError):
            listener = listeners.Route()
            listener(self.create_event(PATH_INFO='/test'))


class TestDispatchExecuteListener(object):

    def test_execute(self):
        with raises(InternalServerError):
            route = LiteralRoute('test', path='/')
            match = RouteMatch(route, {})
            event = Event('something', params={'context': {'route_match': match}})
            listener = listeners.DispatchExecute({'404': 'page/404'})
            listener(event)

    def test_short_circuit(self):
        environ = sample_environ()
        route = LiteralRoute(
            'test',
            path='/',
            options={'controller': 'tests.watson.framework.support.ShortCircuitedController'})
        match = RouteMatch(route, {})
        context = {'request': Request.from_environ(environ), 'route_match': match}
        event = Event(
            'something',
            params={'container': IocContainer(), 'context': context})
        listener = listeners.DispatchExecute({'404': 'page/404'})
        response, view_model = listener(event)
        assert isinstance(response, Response)

    def test_returned_view_model(self):
        environ = sample_environ()
        route = LiteralRoute(
            'test',
            path='/',
            options={'controller': 'tests.watson.framework.support.SampleActionController'})
        match = RouteMatch(route, {'action': 'view_model'})
        context = {'request': Request.from_environ(environ), 'route_match': match}
        event = Event(
            'something',
            params={'container': IocContainer(), 'context': context})
        listener = listeners.DispatchExecute({'404': 'page/404'})
        response, view_model = listener(event)
        assert isinstance(view_model, views.Model)
        assert view_model.template == 'sampleactioncontroller/view_model'

    def test_overriden_template(self):
        environ = sample_environ()
        route = LiteralRoute(
            'test',
            path='/',
            options={'controller': 'tests.watson.framework.support.SampleActionController'})
        match = RouteMatch(route, {'action': 'view_model_template'})
        context = {'request': Request.from_environ(environ), 'route_match': match}
        event = Event(
            'something',
            params={'container': IocContainer(), 'context': context})
        listener = listeners.DispatchExecute({'404': 'page/500'})
        response, view_model = listener(event)
        assert isinstance(view_model, views.Model)
        assert view_model.template == 'sampleactioncontroller/404'


class TestExceptionListener(object):
    pass


class TestRenderListener(object):
    def test_execute(self):
        app = applications.Http()
        listener = listeners.Render(config.views)
        context = {
            'response': Response(200),
        }
        vm = views.Model(format='text/plain', data={'content': 'test'})
        params = {'context': context, 'view_model': vm, 'container': app.container}
        event = Event('render', params=params)
        # error raised as no template exists
        with raises(InternalServerError):
            listener(event)
        with raises(InternalServerError):
            vm.format = 'exe'
            listener(event)
        vm.format = 'json'
        response = listener(event)
        assert response.status_code == 200
        assert response.headers['Content-Type'] == 'application/json'
