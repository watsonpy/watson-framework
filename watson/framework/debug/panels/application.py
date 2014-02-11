# -*- coding: utf-8 -*-
import pprint
import pygments
from pygments import formatters, lexers
import resource
from watson.framework.debug import abc
from watson.framework import events

TEMPLATE = """
<dt>Controller:</dt>
<dd>{{ controller }}</dd>
<dt>Route:</dt>
<dd>{{ route_name }}</dd>
<dt>Template:</dt>
<dd>{{ template }}</dd>
<dt>Memory Usage:</dt>
<dd>{{ usage }}mb</dd>
<dt>Configuration</dt>
<dd>{{ config }}</dd>
"""


class Panel(abc.Panel):
    title = 'Application'
    route_match = None

    @property
    def route_name(self):
        return self.route_match.route.name if self.route_match else None

    @property
    def controller(self):
        return self.route_match.route.options['controller'] if self.route_match else ''

    @property
    def template(self):
        return self.view_model.template

    @property
    def usage(self):
        return round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1000 / 1024, 2)

    def register_listeners(self):
        self.application.dispatcher.add(events.DISPATCH_EXECUTE, self.route_match_listener)
        self.application.dispatcher.add(events.RENDER_VIEW, self.render_listener, 1000)

    def route_match_listener(self, event):
        self.route_match = event.params['context']['route_match']

    def render_listener(self, event):
        self.view_model = event.params['view_model']

    def render(self):
        return self.renderer.env.from_string(TEMPLATE).render(
            route_name=self.route_name,
            controller=self.controller,
            template=self.template,
            usage=self.usage,
            config=pygments.highlight(pprint.pformat(self.application.config), lexers.PythonLexer(), formatters.HtmlFormatter()))

    def render_key_stat(self):
        return '{0}mb'.format(self.usage)
