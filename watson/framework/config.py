# -*- coding: utf-8 -*-
# Default configuration for a Watson application.
# The container itself can be referenced by a simple lambda function such as:
# lambda container: container
#
# Consult the documentation for more indepth setting information.
import os
from watson.framework import events

# Debug settings
debug = {
    'enabled': False,
    'icons_only': False,
    'panels': {
        'watson.framework.debug.panels.Request': {
            'enabled': True
        },
        'watson.framework.debug.panels.Application': {
            'enabled': True
        },
        'watson.framework.debug.panels.Profile': {
            'enabled': True,
            'max_results': 20,
            'sort': 'time',
        },
        'watson.framework.debug.panels.Framework': {
            'enabled': True
        },
        'watson.framework.debug.panels.Logging': {
            'enabled': True
        }
    }
}

# IocContainer settings
dependencies = {
    'definitions': {
        'shared_event_dispatcher':
        {'item': 'watson.events.dispatcher.EventDispatcher'},
        'router': {
            'item': 'watson.routing.routers.DictRouter',
            'init':
            [lambda container: container.get(
             'application.config').get('routes', None)]
        },
        'profiler': {
            'item': 'watson.framework.debug.profilers.Profiler',
            'init':
            [lambda container: container.get(
             'application.config')['debug']['profiling']]
        },
        'exception_handler': {
            'item': 'watson.framework.exceptions.ExceptionHandler',
            'init':
            [lambda container: container.get(
             'application.config').get('debug', {})]
        },
        'jinja2_renderer': {
            'item': 'watson.framework.views.renderers.jinja2.Renderer',
            'init': [
                lambda container: container.get('application.config')[
                    'views']['renderers']['jinja2'].get('config', {}),
                lambda container: container.get('application')
            ]
        },
        'json_renderer': {'item': 'watson.framework.views.renderers.json.Renderer'},
        'xml_renderer': {'item': 'watson.framework.views.renderers.xml.Renderer'},
        'app_dispatch_execute_listener': {
            'item': 'watson.framework.listeners.DispatchExecute',
            'init':
            [lambda container: container.get(
             'application.config')['views']['templates']]
        },
        'app_exception_listener': {
            'item': 'watson.framework.listeners.Exception_',
            'init': [
                lambda container: container.get('exception_handler'),
                lambda container: container.get(
                    'application.config')['views']['templates']
            ]
        },
        'app_render_listener': {
            'item': 'watson.framework.listeners.Render',
            'init':
            [lambda container: container.get('application.config')['views']]
        },
        'translator': {
            'item': 'watson.framework.i18n.translate.Translator',
            'init': [
                lambda container: container.get(
                    'application.config')['i18n']['default_locale'],
                lambda container: container.get(
                    'application.config')['i18n']['package']
            ]
        },
        'mailer_backend': {
            'item': lambda container: container.get('application.config')['mail']['backend']['class'],
            'init': lambda container: container.get('application.config')['mail']['backend']['options']
        },
        'mailer': {
            'item': 'watson.framework.mail.Mailer',
            'init': [
                lambda container: container.get('mailer_backend'),
                lambda container: container.get(
                    container.get('application.config')['views']['renderers'][container.get(
                        'application.config')['views']['default_renderer']]['name']),
            ]
        }
    }
}

# View settings
views = {
    'default_format': 'html',
    'default_renderer': 'jinja2',
    'renderers': {
        'jinja2': {
            'name': 'jinja2_renderer',
            'config': {
                'extension': 'html',
                'paths': [os.path.join(os.getcwd(), 'views')],
                'packages': [],
                'framework_packages': [
                    ('watson.framework.views.templates', 'html'),
                    ('watson.framework.debug', 'views'),
                ],
                'filters': ['watson.framework.support.jinja2.filters'],
                'globals': ['watson.framework.support.jinja2.globals'],
            }
        },
        'xml': {'name': 'xml_renderer'},
        'json': {'name': 'json_renderer'}
    },
    'templates': {
        '404': 'errors/404',
        '500': 'errors/500'
    }
}

# Logging settings
logging = {
    'callable': 'logging.config.dictConfig',
    'ignore_status': (404,),
    'options': {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(process)d %(thread)d - %(message)s'
            },
            'simple': {
                'format': '%(asctime)s - %(levelname)s - %(message)s'
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'DEBUG',
                'formatter': 'verbose',
                'stream': 'ext://sys.stdout'
            },
        },
        'loggers': {},
        'root': {
            'level': 'DEBUG',
            'handlers': ['console']
        }
    }
}

# Session settings
session = {
    'class': 'watson.http.sessions.File',
    'options': {
        'timeout': 3600
    }
}

# Exceptions
exceptions = {
    'class': 'watson.framework.exceptions.ApplicationError'
}

# Localization
i18n = {
    'default_locale': 'en',
    'package': 'watson.framework.i18n.locales'
}

# Mail
mail = {
    'backend': {
        'class': 'watson.mail.backends.Sendmail',
        'options': {}
    },
}

# Components
components = []

# Application event settings
events = {
    events.EXCEPTION: [('app_exception_listener',)],
    events.INIT: [
        ('watson.framework.logging.listeners.Init', 1),
        ('watson.framework.debug.listeners.Init', 1)
    ],
    events.ROUTE_MATCH: [('watson.framework.listeners.Route',)],
    events.DISPATCH_EXECUTE: [('app_dispatch_execute_listener',)],
    events.RENDER_VIEW: [('app_render_listener',)],
}
