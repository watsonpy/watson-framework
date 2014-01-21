# -*- coding: utf-8 -*-
from wsgiref import util
from pytest import raises
from watson.di.container import IocContainer
from watson.events.types import Event
from watson.http.messages import create_request_from_environ, Response
from watson.framework.routing import Router, RouteMatch, Route
from watson.framework.exceptions import NotFoundError, InternalServerError
from watson.framework import listeners
from tests.watson.framework.support import sample_environ


class TestBaseListener(object):

    def test_missing_call(self):
        with raises(TypeError):
            listeners.Base()


class TestRouteListener(object):

    def create_event(self, **kwargs):
        router = Router({'home': {'path': '/'}})
        environ = {}
        util.setup_testing_defaults(environ)
        environ.update(**kwargs)
        event = Event(
            'TestEvent',
            params={'router': router,
                    'request': create_request_from_environ(environ)})
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
            route = Route('test', path='/')
            match = RouteMatch(route, {})
            event = Event('something', params={'route_match': match})
            listener = listeners.DispatchExecute({'404': 'page/404'})
            listener(event)

    def test_short_circuit(self):
        environ = sample_environ()
        route = Route(
            'test',
            path='/',
            options={'controller': 'tests.watson.framework.support.ShortCircuitedController'})
        match = RouteMatch(
            route,
            {'controller': 'tests.watson.framework.support.ShortCircuitedController'})
        event = Event(
            'something',
            params={'route_match': match,
                    'container': IocContainer(),
                    'request': create_request_from_environ(environ)})
        listener = listeners.DispatchExecute({'404': 'page/404'})
        response = listener(event)
        assert isinstance(response, Response)


class TestExceptionListener(object):
    pass


class TestRenderListener(object):
    pass
