# -*- coding: utf-8 -*-
import pygments
from pygments import formatters, lexers
import resource
from watson.framework.debug import abc
from watson.framework import events


def pretty(value, htchar='    ', lfchar='\n', indent=0):
    """Print out a dictionary as a string.
    """
    nlch = lfchar + htchar * (indent + 1)
    if isinstance(value, dict):
        items = [
            nlch + repr(key) + ': ' + pretty(
                value[key], htchar, lfchar, indent + 1)
            for key in sorted(value)
        ]
        return '{{{}}}'.format((','.join(items) + lfchar + htchar * indent))
    elif isinstance(value, (list, tuple)):
        items = [
            nlch + pretty(item, htchar, lfchar, indent + 1)
            for item in value
        ]
        lchar = '['
        rchar = ']'
        if isinstance(value, tuple):
            lchar = '('
            rchar = ')'
        return '{}{}{}'.format(
            lchar, (','.join(items) + lfchar + htchar * indent), rchar)
    else:
        return repr(value)


class Panel(abc.Panel):
    title = 'Application'
    icon = 'cube'
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
        return self._render({
            'route_name': self.route_name,
            'controller': self.controller,
            'template': self.template,
            'usage': self.usage,
            'config': pygments.highlight(
                pretty(self.application.config),
                lexers.PythonLexer(),
                formatters.HtmlFormatter(cssclass='codehilite'))
        })

    def render_key_stat(self):
        return '{0}mb'.format(self.usage)
