# -*- coding: utf-8 -*-
from pytest import raises
from tests.watson.framework.debug import support
from watson.framework import applications


class TestAbc(object):
    def test_panel(self):
        p = support.SamplePanel({}, None, applications.Http())
        with raises(NotImplementedError):
            str(p)
        with raises(NotImplementedError):
            p.render_key_stat()
