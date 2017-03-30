# -*- coding: utf-8 -*-
from watson.framework import applications
from watson.framework.debug.panels import Logging


class TestLogging(object):
    def setup(self):
        app = applications.Http()
        p = Logging(
            {'enabled': True}, app.container.get('jinja2_renderer'), app)
        self.app = app
        self.panel = p

    def test_render(self):
        assert 'watson-debug-toolbar__panel__log' in self.panel.render()

    def test_render_key_stat(self):
        assert self.panel.render_key_stat() == '0 messages'
