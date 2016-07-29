# -*- coding: utf-8 -*-
from watson.framework.debug import abc


class Panel(abc.Panel):
    title = 'Request'
    icon = 'globe'

    def render(self):
        return self._render({
            'request': self.event.params['context']['request']
        })

    def render_key_stat(self):
        return self.event.params['context']['request'].method
