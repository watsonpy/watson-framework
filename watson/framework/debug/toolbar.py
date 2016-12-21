# -*- coding: utf-8 -*-
import collections
from watson.common import imports
from watson.framework import events


class Toolbar(object):
    config = None
    panels = None
    replace_tag = '</body>'

    def __init__(self, config, application, renderer):
        """Application can be any WSGI callable
        """
        self.application = application
        self.config = config
        self.renderer = renderer
        self.panels = collections.OrderedDict()
        for module, settings in config['panels'].items():
            if settings['enabled']:
                panel = imports.load_definition_from_string(
                    module)(settings, renderer, application)
                panel.register_listeners()
                self.panels[panel.title] = panel

    def register_listeners(self):
        self.application.dispatcher.add(events.RENDER_VIEW, self.render, -1000)

    def render(self, event):
        """Render the toolbar to the browser.
        """
        for module, panel in self.panels.items():
            panel.event = event
        context = event.params['context']
        response, view_model = context['response'], event.params['view_model']
        if view_model.format == 'html':
            html_body = ''.join([
                self.renderer.render(
                    'debug/toolbar',
                    {'panels': self.panels, 'config': self.config}),
                self.replace_tag])
            response.body = response.body.replace(self.replace_tag, html_body)
        return response
