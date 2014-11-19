# -*- coding: utf-8 -*-
from watson.di import ContainerAware
from watson.framework import applications
from watson.framework.debug import Toolbar


class Init(ContainerAware):

    """Attaches itself to the applications INIT event and initializes the toolbar.
    """

    def __call__(self, event):
        app = event.target
        if isinstance(app, applications.Http):
            debug_config = app.config['debug']
            if debug_config['enabled'] and debug_config.get('toolbar'):
                toolbar = Toolbar(
                    app.config['debug'],
                    app,
                    self.container.get('jinja2_renderer'))
                toolbar.register_listeners()
                return toolbar
