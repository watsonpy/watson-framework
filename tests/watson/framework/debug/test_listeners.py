# -*- coding: utf-8 -*-
from watson.events import types
from watson.framework import applications
from watson.framework.debug import listeners, toolbar


class TestInit(object):
    def test_execute(self):
        app = applications.Http({
            'debug': {
                'enabled': True,
                'toolbar': {'bar': ''}
            }
        })
        event = types.Event('test', target=app)
        listener = listeners.Init()
        listener.container = app.container
        tb = listener(event)
        assert isinstance(tb, toolbar.Toolbar)
