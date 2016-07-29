# -*- coding: utf-8 -*-
from watson.framework.debug import abc, profile


class Panel(abc.Panel):
    title = 'Profile'
    icon = 'clock-o'

    def __init__(self, config, renderer, application):
        super(Panel, self).__init__(config, renderer, application)
        if config.get('enabled'):
            self.application_run = application.run
            application.run = self.run

    def render(self):
        return self._render({
            'times': self.data.get('times', []),
            'total_time': self.data.get('total_time', 0),
            'function_calls': self.data.get('function_calls', 0),
            'primative_calls': self.data.get('primative_calls', 0)
        })

    def render_key_stat(self):
        return '{0}s'.format(self.data.get('total_time', 0))

    def run(self, environ, start_response):
        response, stats = profile.execute(self.application_run,
                                          sort_order=self.config['sort'],
                                          max_results=self.config['max_results'],
                                          environ=environ, start_response=start_response)
        self.data = stats
        return response
