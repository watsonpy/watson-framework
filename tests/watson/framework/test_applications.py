# -*- coding: utf-8 -*-
from pytest import raises
from watson.di.container import IocContainer
from watson.framework import applications, config, exceptions
from watson.common.datastructures import module_to_dict
from watson.http.messages import Request
from tests.watson.framework.support import sample_environ, start_response, SampleNonStringCommand
from tests.watson.framework import sample_config


class TestBaseApplication(object):

    def test_call(self):
        with raises(TypeError):
            applications.Base()


class TestHttpApplication(object):

    def test_create(self):
        application = applications.Http()
        assert isinstance(application.container, IocContainer)
        assert application.config == module_to_dict(config, '__')
        application_module = applications.Http(sample_config)
        assert application_module.config['debug']['enabled']

    def test_call(self):
        application = applications.Http({
            'routes': {
                'home': {
                    'path': '/',
                    'options': {
                        'controller': 'tests.watson.framework.support.TestController'
                    },
                    'requires': {
                        'format': 'json'
                    }
                }
            },
            'views': {
                'templates': {
                    'watson/mvc/test_applications/testcontroller/post': 'blank'
                }
            },
            'debug': {
                'enabled': True
            }
        })
        environ = sample_environ(PATH_INFO='/',
                                 REQUEST_METHOD='POST',
                                 HTTP_ACCEPT='application/json')
        response = application(environ, start_response)
        assert response == [b'{"content": "Posted Hello World!"}']

    def test_raise_exception_event_not_found(self):
        application = applications.Http()
        response = application(sample_environ(PATH_INFO='/'), start_response)
        assert '<h1>Not Found</h1>' in response[0].decode('utf-8')

    def test_raise_exception_event_server_error(self):
        application = applications.Http({
            'routes': {
                'home': {
                    'path': '/',
                    'options': {
                        'controller': 'tests.watson.framework.support.TestController'
                    }
                }
            }
        })
        response = application(sample_environ(PATH_INFO='/'), start_response)
        assert '<h1>Internal Server Error</h1>' in response[0].decode('utf-8')

    def test_application_logic_error(self):
        application = applications.Http({
            'routes': {
                'home': {
                    'path': '/',
                    'options': {
                        'controller':
                            'tests.watson.framework.support.SampleActionController',
                        'action': 'blah_syntax_error'
                    }
                }
            },
            'views': {
                'templates': {
                    'watson/mvc/test_applications/testcontroller/blah_syntax_error':
                    'blank'
                }
            }
        })
        response = application(sample_environ(PATH_INFO='/'), start_response)
        assert '<h1>Internal Server Error</h1>' in response[0].decode('utf-8')

    def test_no_exception_class(self):
        app = applications.Http({'exceptions': None})
        assert app.exception_class is exceptions.ApplicationError

    def test_no_dispatcher_render(self):
        with raises(KeyError):
            # No context specified
            app = applications.Http()
            app.render(with_dispatcher=False)

    def test_last_exception(self):
        # occurs when exceptions have been raised from others
        environ = sample_environ()
        context = {
            'request': Request.from_environ(environ)
        }
        app = applications.Http()
        response, view_model = app.exception(
            last_exception=True, exception=Exception('test'), context=context)
        assert '<h1>Internal Server Error</h1>' in response.body


class TestConsoleApplication(object):

    def test_create(self):
        application = applications.Console()
        assert isinstance(application.container, IocContainer)

    def test_register_commands(self):
        application = applications.Console({
            'commands': ['tests.watson.framework.support.SampleStringCommand',
                         SampleNonStringCommand]
        })
        assert len(application.config['commands']) == 4

    def test_execute_command(self):
        application = applications.Console({
            'commands': ['tests.watson.framework.support.SampleStringCommand',
                         SampleNonStringCommand]
        })
        assert application(['py.test', 'string', 'execute']) == 'Executed!'
        assert not application.get_command('test')
