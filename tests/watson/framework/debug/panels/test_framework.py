# -*- coding: utf-8 -*-
from watson.framework import applications
from watson.framework.debug.panels import Framework


class TestFramework(object):
    def setup(self):
        app = applications.Http()
        p = Framework(
            {'enabled': True}, app.container.get('jinja2_renderer'), app)
        self.app = app
        self.panel = p

    def test_render(self):
        assert '<dt>Version:</dt>' in self.panel.render()

    def test_render_key_stat(self):
        assert self.panel.render_key_stat().startswith('v')
