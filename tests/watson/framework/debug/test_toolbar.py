# -*- coding: utf-8 -*-
from watson.events import types
from watson.framework.debug import toolbar
from watson.framework import views, applications
from watson.http import messages


class TestToolbar(object):
    def test_render(self):
        app = applications.Http()
        tb = toolbar.Toolbar(
            {
                'panels': {
                    'tests.watson.framework.debug.support.Panel': {'enabled': True}
                }
            },
            app, app.container.get('jinja2_renderer'))
        params = {
            'context': {
                'request': messages.Request.from_environ({}),
                'response': messages.Response(200, body='<html><body></body></html>')
            },
            'view_model': views.Model(format='html')
        }
        event = types.Event('render', params=params)
        response = tb.render(event)
        assert '<!-- Injected Watson Debug Toolbar -->' in response.body
