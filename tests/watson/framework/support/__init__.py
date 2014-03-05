# -*- coding: utf-8 -*-
# Support functions, classes
from wsgiref import util
from watson.console import command
from watson.http.messages import Response
from watson.framework import controllers
from watson.framework.views import Model


def start_response(status_line, headers):
    pass


def sample_environ(**kwargs):
    environ = {}
    util.setup_testing_defaults(environ)
    environ.update(kwargs)
    return environ


class SampleActionController(controllers.Action):

    def something_action(self, **kwargs):
        return 'something_action'

    def blah_action(self, **kwargs):
        return 'blah_action'

    def blah_syntax_error_action(self):
        a = b

    def blank_action(self, **kwargs):
        pass

    def kwargs_missing_action(self):
        raise Exception('Exception related to the code')

    def exception_action(self, **kwargs):
        raise TypeError('Exception related to the code')

    def do_forward(self):
        return self.forward(SampleActionController(), method='forwarded')

    def do_method_forward(self):
        return self.forward('tests.watson.framework.support.AnotherSampleActionController')

    def forwarded(self):
        return 'Response'

    def view_model_action(self, **kwargs):
        return Model(data='test')

    def view_model_template_action(self, **kwargs):
        return Model(data='test', template='404')


class AnotherSampleActionController(controllers.Action):
    def do_method_forward(self):
        return 'Another Response'


class ShortCircuitedController(controllers.Rest):

    def GET(self):
        return Response(body='testing')


class SampleRestController(controllers.Rest):

    def GET(self, **kwargs):
        return 'GET'


def sample_view_model():
    return (
        Model(
            format='html', template=None, data={"test": {"nodes": {"node": ["Testing", "Another node"]}}})
    )


class TestController(controllers.Rest):

    def GET(self, **kwargs):
        return 'Hello World!'

    def POST(self, **kwargs):
        return 'Posted Hello World!'


class SampleNonStringCommand(command.Base):
    name = 'nonstring'


class SampleStringCommand(command.Base):
    name = 'string'

    def execute(self):
        return 'Executed!'
