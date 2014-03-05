# -*- coding: utf-8 -*-
from watson.events import types
from watson.framework import applications
from watson.framework.debug.panels import Request
from watson.http import messages
from tests.watson.framework import support


class TestRequest(object):
    def setup(self):
        app = applications.Http()
        p = Request(
            {'enabled': True}, app.container.get('jinja2_renderer'), app)
        self.app = app
        self.panel = p
        params = {
            'context': {
                'request': messages.Request.from_environ(support.sample_environ())
            }
        }
        p.event = types.Event('test', params=params)

    def test_render(self):
        assert '<dt>Method:</dt>' in self.panel.render()

    def test_render_key_stat(self):
        assert self.panel.render_key_stat() == 'GET'
