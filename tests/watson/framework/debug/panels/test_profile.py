# -*- coding: utf-8 -*-
from watson.framework import applications
from watson.framework.debug.panels import Profile
from tests.watson.framework import support


class TestProfile(object):
    def setup(self):
        app = applications.Http()
        p = Profile(
            {'enabled': True, 'sort': 'time', 'max_results': 20},
            app.container.get('jinja2_renderer'), app)
        self.app = app
        self.panel = p

    def test_render(self):
        assert '<th>Times</th>' in self.panel.render()

    def test_render_key_stat(self):
        assert self.panel.render_key_stat().endswith('s')

    def test_run(self):
        response = self.panel.run(
            support.sample_environ(), support.start_response)
        assert isinstance(response[0], bytes)
