# -*- coding: utf-8 -*-
from watson.framework import applications
from watson.framework.support.jinja2.globals import (url, config, request,
                                                     flash_messages, _)


class TestGlobals(object):
    def test_url(self):
        app = applications.Http({
            'routes': {
                'home': {
                    'path': '/'
                }
            }
        })
        u = url(router=app.container.get('router'))
        assert u('home') == '/'
        assert u('home', host='127.0.0.1') == '127.0.0.1/'
        assert u('home', host='127.0.0.1', scheme='https') == 'https://127.0.0.1/'

    def test_config(self):
        app = applications.Http()
        c = config(application=app)
        assert c()['views']

    def test_request(self):
        assert request({'context': {'request': 'test'}}) == 'test'

    def test_flash_messages(self):
        assert not flash_messages({'context': {}})
        assert flash_messages({'context': {'flash_messages': ['test']}}) == ['test']

    def test_translate(self):
        app = applications.Http({
            'i18n': {
                'package': 'tests.watson.framework.i18n.locales'
            }
        })
        translate = _(app.container.get('translator'))
        assert translate('test.string') == 'This is a sample string'
