.. _configuration:

Configuration
=============

Introduction
------------
While Watson is primarily built with convention over configuration in mind, there are still plenty of configuration options that can be modified to override the default behaviour.

.. note::
   To override values within the default configuration, you only need to replace those values within your own configuration file. The application with automatically merge the defaults with your new options.

Application Configuration
-------------------------
Configuration for Watson is just a standard python module (and should be familiar to those who have used Django previously). Available keys for configuration are:

- debug
- dependencies
- views
- session
- events
- logging

You can see the default configuration that Watson uses within the ``watson.framework.config`` module.

Debug
-----

Debug is responsible for determining if the application is running in debug mode, and the relevant profiling settings.

*watson.framework.config*

.. code-block:: python

   debug = {
      'enabled': False,
      'panels': {
         'watson.debug.panels.request.Panel': {
            'enabled': True
         },
         'watson.debug.panels.application.Panel': {
            'enabled': True
         },
         'watson.debug.panels.profile.Panel': {
            'enabled': True,
            'max_results': 20,
            'sort': 'time',
         },
         'watson.debug.panels.framework.Panel': {
            'enabled': True
         },
      }
   }

Dependencies
------------

The configuration of your application will automatically be added to the container, which can then be retrieved via the key ``application.config``.

See the dependency injection :ref:`key_concepts` for more information on how to define dependencies and container parameters.

Views
-----

Watson utilizes multiple renderers to output the different views that the user may request. Each renderer is retrieved from the dependency injection container (see above), with the name key being the same as the relevant dependency name.

*watson.framework.config*

.. code-block:: python

   views = {
       'default_format': 'html',
       'renderers': {
           'default': {
               'name': 'jinja2_renderer',
               'config': {
                   'extension': 'html',
                   'paths': [os.path.join(os.getcwd(), 'views')]
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

The above configuration sets the default renderer to use Jinja2. It also specifies two other renderers, which will output XML and JSON respectively. There are also a set of templates defined, which allows you to override templates that will be used. The format of these being 'existing template path': 'new template path' (relative to the views directory).

Session
-------

By default Watson will use File for session storage, which stores the contents of each session in their own file within your systems temporary directory (unless otherwise specified in the config).

*watson.framework.config*

.. code-block:: python

   session = {
       'class': 'watson.http.sessions.File',
       'options': {}  # a dict of options for the storage class
   }

See the storage methods that are available for sessions in the :ref:`reference_library`.

Events
------

Events are the core to the lifecycle of both a request and the initialization of a Watson application. The default configuration sets up 5 events which will be executed at different times of the lifecycle.

*watson.framework.config*

.. code-block:: python

   events = {
       events.EXCEPTION: [('app_exception_listener',)],
       events.INIT: [
           ('watson.debug.profilers.ApplicationInitListener', 1, True)
       ],
       events.ROUTE_MATCH: [('watson.framework.listeners.RouteListener',)],
       events.DISPATCH_EXECUTE: [('app_dispatch_execute_listener',)],
       events.RENDER_VIEW: [('app_render_listener',)],
   }

Logging
-------

Watson will automatically catch all exceptions thrown by your application. You can configure the logging exactly how you would using the standard libraries logging module.

.. code-block:: python

   logging = {
       'callable': 'logging.config.dictConfig',
       'ignore_status': {
           '404': True
       },
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

The callable key allows you to change the way the logging it to be configured, in case you want to use a different method for logging. ignore_status allows you to ignore specific status codes from being logged (chances are you don't want to log 404 errors).

A common logging setup may look similar to the following:

.. code-block:: python

   logging = {
       'options': {
           'handlers': {
               'error_file_handler': {
                   'class': 'logging.handlers.RotatingFileHandler',
                   'level': 'DEBUG',
                   'formatter': 'verbose',
                   'filename': '../data/logs/error.log',
                   'maxBytes': 10485760,
                   'backupCount': '20',
                   'encoding': 'utf8'
               },
           },
           'loggers': {
               'my_app': {
                   'level': 'DEBUG',
                   'handlers': ['error_file_handler']
               },

           },
       }
   }

Integrating Sentry
^^^^^^^^^^^^^^^^^^

Sentry is a great piece of software that allows you to aggregrate your error logs. Integrating it into Watson is straightfoward, and only requires modifying the configuration of your application.

.. code-block:: python

   logging = {
       'options': {
           'handlers': {
               'sentry': {
                   'dsn': 'http://SENTRY_DSN_URL_GOES_HERE',
               },
           },
           'loggers': {
               'my_app': {
                   'level': 'DEBUG',
                   'handlers': ['sentry']
               }
           }
       }
   }

If you'd like to have Sentry be used for every exception, the following will work:

.. code-block:: python

    logging = {
        'options': {
            'handlers': {
                'sentry': {
                    'dsn': 'http://SENTRY_DSN_URL_GOES_HERE',
                },
            },
            'root': {
                'handlers': ['console', 'sentry']
            }
        }
    }

You can then access the logger from within your app with the following code:

.. code-block:: python

   import logging
   logger = logging.getLogger(__name__)
   logger.error('Something has gone wrong')

Extending the Configuration
---------------------------

There are times when you may want to allow other developers to get access to your configuration from dependencies retrieved from the container. This can easily be achieved by the use of lambda functions.

First create the settings you wish to retrieve in your settings:

*app/config/config.py*

.. code-block:: python

   my_class_config = {
       'a_setting': 'a value'
   }

And then within your dependency definitions you can reference it like this:

*app/config/config.py*

.. code-block:: python

   dependencies = {
       'definitions': {
           'my_class': {
               'item': 'my.module.Klass',
               'init': [lambda ioc: ioc.get('application.config')['my_class_config']]
           }
       }
   }

When my.module.Klass is initialized, the configuration settings will be passed as the first argument to the __init__ method.
