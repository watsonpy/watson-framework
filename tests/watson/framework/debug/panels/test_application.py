# -*- coding: utf-8 -*-
from watson.events import types
from watson.framework import applications, views
from watson.framework.debug.panels import Application
from watson.routing import routes


class TestApplication(object):
    def setup(self):
        app = applications.Http()
        p = Application(
            {'enabled': True}, app.container.get('jinja2_renderer'), app)
        self.app = app
        self.panel = p

    def test_route_name(self):
        assert not self.panel.route_name
        self.panel.route_match = routes.RouteMatch(
            routes.LiteralRoute('test', '/'), {})
        assert self.panel.route_name == 'test'

    def test_controller(self):
        assert not self.panel.controller
        self.panel.route_match = routes.RouteMatch(
            routes.LiteralRoute('test', '/', options={'controller': 'test'}), {})
        assert self.panel.controller == 'test'

    def test_template(self):
        self.panel.view_model = views.Model(template='test')
        assert self.panel.template == 'test'

    def test_usage(self):
        assert self.panel.usage > 0

    def test_route_match_listener(self):
        rm = routes.RouteMatch('test', {})
        params = {
            'context': {'route_match': rm}
        }
        event = types.Event('name', params=params)
        self.panel.route_match_listener(event)
        assert self.panel.route_match is rm

    def test_render_listener(self):
        vm = views.Model()
        params = {
            'view_model': vm
        }
        event = types.Event('name', params=params)
        self.panel.render_listener(event)
        assert self.panel.view_model is vm

    def test_render(self):
        self.panel.view_model = views.Model(format='html')
        output = self.panel.render()
        assert '<dt>Memory Usage:</dt>' in output

    def test_key_stat(self):
        assert self.panel.render_key_stat().endswith('mb')
