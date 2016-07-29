# -*- coding: utf-8 -*-
from watson import framework
from watson.framework.debug import abc


class Panel(abc.Panel):
    title = 'Framework'
    icon = 'code'

    def render(self):
        return self._render({
            'version': framework.__version__,
            'events': self.application.dispatcher.events
        })

    def render_key_stat(self):
        return 'v{0}'.format(framework.__version__)
