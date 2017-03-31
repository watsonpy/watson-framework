# -*- coding: utf-8 -*-
from watson.framework.views.renderers.xml import Renderer as Xml
from watson.framework.views.renderers.json import Renderer as Json
from watson.framework.views.renderers.jinja2 import Renderer as Jinja2, template_to_posix_path
from watson.framework import applications
from watson.http import messages
from tests.watson.framework.support import sample_view_model, sample_object_view_model


class TestXmlRenderer(object):

    def test_output(self):
        renderer = Xml()
        output = renderer(sample_view_model())
        assert output == '<?xml version="1.0" encoding="utf-8" ?><test><nodes><node>Testing</node><node>Another node</node></nodes></test>'


class TestJsonRenderer(object):

    def test_output(self):
        renderer = Json()
        output = renderer(sample_view_model())
        assert output == '{"test": {"nodes": {"node": ["Testing", "Another node"]}}}'

    def test_output_serialized_object(self):
        renderer = Json()
        output = renderer(sample_object_view_model())
        assert output == '{"name": "value"}'

    def test_output_error(self):
        message = messages.Response(status_code=500)
        renderer = Json()
        vm = sample_view_model()
        vm.data['debug'] = False
        output = renderer._formatted_error(vm, context={'response': message})
        assert output['name'] == 'Unknown Error'


class TestJinja2Renderer(object):

    def test_output(self):
        app = applications.Http({
            'debug': {'enabled': True},
        })
        renderer_config = app.config['views']['renderers']['jinja2']['config']
        renderer = Jinja2(config=renderer_config, application=app)
        assert renderer._debug_mode

    def test_posix_path(self):
        assert template_to_posix_path('some/template') == 'some/template'
        assert template_to_posix_path('some\\template', sep='\\') == 'some/template'
