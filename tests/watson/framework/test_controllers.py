# -*- coding: utf-8 -*-
from io import BytesIO, BufferedReader
from pytest import raises
from unittest.mock import Mock
from watson.events import types
from watson.http.messages import Request, Response
from watson.framework import controllers
from watson.routing.routers import DictRouter
from tests.watson.framework.support import SampleActionController, SampleRestController, sample_environ


class TestNotImplementedController(object):

    def test_execute_invalid(self):
        with raises(TypeError):
            controllers.Base()


class TestBaseHttpController(object):

    def test_request_response(self):
        base = controllers.HttpMixin()
        base.request = Request.from_environ(sample_environ())
        assert isinstance(base.request, Request)
        assert isinstance(base.response, Response)

    def test_get_event(self):
        base = controllers.HttpMixin()
        base.event = types.Event('test')
        assert isinstance(base.event, types.Event)

    def test_set_event(self):
        with raises(TypeError):
            base = controllers.HttpMixin()
            base.event = 'test'

    def test_invalid_request(self):
        with raises(TypeError):
            base = controllers.HttpMixin()
            base.request = 'test'

    def test_invalid_response(self):
        with raises(TypeError):
            base = controllers.HttpMixin()
            base.response = 'test'

    def test_route_to_url(self):
        base = controllers.HttpMixin()
        router = DictRouter({
            'test': {
                'path': '/test',
            },
            'segment': {
                'path': '/segment[/:part]',
                'type': 'segment'
            }
        })
        base.container = Mock()
        base.container.get.return_value = router
        assert base.url('test') == '/test'
        assert base.url('segment', part='test') == '/segment/test'
        assert base.url('test', host='test.com') == 'test.com/test'
        assert base.url('test', host='test.com', scheme='https://') == 'https://test.com/test'

    def test_redirect(self):
        base = controllers.HttpMixin()
        router = DictRouter({
            'test': {
                'path': '/test',
            },
            'segment': {
                'path': '/segment[/:part]',
                'type': 'segment',
                'defaults': {'part': 'test'}
            }
        })
        base.request = Request.from_environ(sample_environ())
        base.container = Mock()
        base.container.get.return_value = router
        response = base.redirect('/test')
        assert response.headers['location'] == '/test'
        response = base.redirect('segment')
        assert response.headers['location'] == '/segment/test'
        assert response.status_code == 302

    def test_post_redirect_get(self):
        base = controllers.HttpMixin()
        router = DictRouter({'test': {'path': '/test'}})
        environ = sample_environ(PATH_INFO='/', REQUEST_METHOD='POST')
        environ['wsgi.input'] = BufferedReader(
            BytesIO(b'post_var_one=test&post_var_two=blah'))
        base.request = Request.from_environ(
            environ, 'watson.http.sessions.Memory')
        base.container = Mock()
        base.container.get.return_value = router
        response = base.redirect('test')
        assert response.status_code == 303
        assert base.redirect_vars == base.request.session['post_redirect_get']
        base.clear_redirect_vars()
        assert not base.redirect_vars
        base.redirect('test', clear=True)
        assert not base.redirect_vars

    def test_flash_message(self):
        controller = SampleActionController()
        controller.request = Request.from_environ(sample_environ(), 'watson.http.sessions.Memory')
        controller.flash_messages.add('testing')
        controller.flash_messages.add('something')
        assert controller.flash_messages['info'] == ['testing', 'something']
        for namespace, message in controller.flash_messages:
            assert namespace == 'info'
        assert not controller.flash_messages.messages

    def test_forward(self):
        controller = SampleActionController()
        request = Request.from_environ(sample_environ())
        context = {'request': request}
        controller.event = types.Event('test', params={'context': context})
        assert controller.do_forward() == 'Response'


class TestActionController(object):

    def test_repr(self):
        controller = SampleActionController()
        assert repr(
            controller) == '<tests.watson.framework.support.SampleActionController>'

    def test_blank_response(self):
        controller = SampleActionController()
        controller.request = Request.from_environ(sample_environ())
        result = controller.execute(action='blank')
        assert isinstance(result, dict)

    def test_execute_result(self):
        controller = SampleActionController()
        assert controller.execute(action='something') == 'something_action'
        assert controller.execute(action='blah') == 'blah_action'

    def test_method_template(self):
        controller = SampleActionController()
        assert controller.get_execute_method_path(
            action='something') == ['sampleactioncontroller', 'something']

    def test_kwargs_missing(self):
        with raises(Exception):
            controller = SampleActionController()
            controller.execute(action='kwargs_missing')

    def tests_exception_occuring_within_action(self):
        with raises(TypeError):
            controller = SampleActionController()
            controller.execute(action='exception')


class TestRestController(object):

    def test_execute_result(self):
        controller = SampleRestController()
        controller.request = Request.from_environ(sample_environ())
        result = controller.execute(something='test')
        assert result == 'GET'

    def test_method_template(self):
        controller = SampleRestController()
        controller.request = Request.from_environ(sample_environ())
        assert controller.get_execute_method_path() == [
            'samplerestcontroller', 'get']


class TestFlashMessageContainer(object):

    def test_create(self):
        session_data = {}
        container = controllers.FlashMessagesContainer(session_data)
        assert len(container) == 0
        assert repr(
            container) == '<watson.framework.controllers.FlashMessagesContainer messages:0>'

    def test_add_messages(self):
        session_data = {}
        container = controllers.FlashMessagesContainer(session_data)
        container.add_messages(['testing'])
        assert len(container) == 1

    def test_set_existing_container(self):
        existing_container = controllers.FlashMessagesContainer({})
        existing_container.add('Test')
        session_data = {'flash_messages': existing_container}
        new_container = controllers.FlashMessagesContainer(session_data)
        assert len(new_container) == 1
