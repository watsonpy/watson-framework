# -*- coding: utf-8 -*-
from watson.framework.debug import abc


class SamplePanel(abc.Panel):
    def render(self):
        return super(SamplePanel, self).render()

    def render_key_stat(self):
        return super(SamplePanel, self).render_key_stat()


class Panel(abc.Panel):
    def render(self):
        return 'Testing'

    def render_key_stat(self):
        return 'Test'
