# -*- coding: utf-8 -*-
from watson.framework.debug import abc, profile

TEMPLATE = """<style>
.watson-debug-toolbar__panel__profile {
    width: 100%;
}
</style>
<table class="watson-debug-toolbar__panel__profile">
    <thead>
        <tr>
            <th>Times</th><th>Total Time</th><th>Per call</th><th>Cumulative Time</th><th>Per call</th><th>Function</th><th>Line</th><th>File</th>
        </tr>
    </thead>
    <tbody>
        {% for time in times %}
        <tr>
            <td>{{ time['number_calls'] }}</td>
            <td>{{ time['total_time'] }}</td>
            <td>{{ time['per_call'] }}</td>
            <td>{{ time['cumulative_time'] }}</td>
            <td>{{ time['per_call2'] }}</td>
            <td>{{ time['file']|e }}</td>
            <td>{{ time['line'] }}</td>
            <td>{{ time['function_name']|e }}</td>
        </tr>
        {% endfor %}
    </tbody>
</table>
"""


class Panel(abc.Panel):
    title = 'Profile'

    def __init__(self, config, renderer, application):
        super(Panel, self).__init__(config, renderer, application)
        if config.get('enabled'):
            self.application_run = application.run
            application.run = self.run

    def render(self):
        return self.renderer.env.from_string(TEMPLATE).render(
            times=self.data.get('times', []),
            total_time=self.data.get('total_time', 0),
            function_calls=self.data.get('function_calls', 0),
            primative_calls=self.data.get('primative_calls', 0))

    def render_key_stat(self):
        return '{0}s'.format(self.data.get('total_time', 0))

    def run(self, environ, start_response):
        response, stats = profile.execute(self.application_run,
                                          sort_order=self.config['sort'],
                                          max_results=self.config['max_results'],
                                          environ=environ, start_response=start_response)
        self.data = stats
        return response
