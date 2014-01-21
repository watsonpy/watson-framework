# -*- coding: utf-8 -*-
from watson.common import imports
from watson.di import ContainerAware


class Init(ContainerAware):

    """Attaches itself to the applications INIT event and initializes the
    logger.
    """

    def __call__(self, event):
        app = event.target
        config = app.config['logging']
        logger_config_callable = imports.load_definition_from_string(
            config['callable'])
        logger_config_callable(config['options'])
