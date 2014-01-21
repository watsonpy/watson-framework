# -*- coding: utf-8 -*-
from pytest import raises
from watson.di.container import IocContainer
from watson.framework import applications, config
from watson.common.datastructures import module_to_dict
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
        response = application(
            sample_environ(PATH_INFO='/',
                           REQUEST_METHOD='POST',
                           HTTP_ACCEPT='application/json'),
            start_response)
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


class TestConsoleApplication(object):

    def test_create(self):
        application = applications.Console()
        assert isinstance(application.container, IocContainer)

    def test_register_commands(self):
        application = applications.Console({
            'commands': ['tests.watson.framework.support.SampleStringCommand',
                         SampleNonStringCommand]
        })
        assert len(application.config['commands']) == 6

    def test_execute_command(self):
        application = applications.Console({
            'commands': ['tests.watson.framework.support.SampleStringCommand',
                         SampleNonStringCommand]
        }, ['py.test', 'string'])
        assert application() == 'Executed!'
        assert not application.get_command('test')
