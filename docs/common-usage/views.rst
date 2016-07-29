.. _common_usage_views:

Views
=====

Views within Watson are considered 'dumb' in that they do not contain any business or application logic within them. The only valid 'logic' that should be contained within a view would be simple for loops, if statements, and similar constructs.

The templating engine prefered by Watson is `Jinja2`_, however this can easily be switched to another engine if required.

.. code-block:: python

    views = {
        'renderers': {
            'default': {
                'name': 'my_new_renderer',
            }
        }
    }

``my_new_renderer`` needs to be configured within the IocContainer to instantiate the new renderer.

Specifying different response formats
-------------------------------------

To output the response in different formats is quite a simple task and only involves modifying the route itself (it can be modified without changing the route, however this is not really encouraged).

.. code-block:: python

    routes = {
        'home': {
            'path': '/',
            'defaults': {
                'format': 'json'
            }
        }
    }

and the subsequent controller...

.. code-block:: python

    from watson.framework import controllers

    class Public(controllers.Rest):
        def GET(self):
            return {'hello': 'world'}

The user can also be made responsible for determining the response format by correctly defining the route to support this. This is particularly useful if you're creating an API and need to support multiple formats such as XML and JSON.

.. code-block:: python

    routes = {
        'home': {
            'path': '/something.:format',
            'requires': {
                'format': 'json|xml'
            }
        }
    }

In the above route, any request being sent to /something.xml or /something.json will output the data in the requested format.

Customizing the view path
By default Watson will try to load views from ``project_name/app_name/views/controller_name/action.html`` where project_name is the name of your project, app_name is the name of your application module, controller_name is the name of the controller that was executed and action is http request method (if the controller is a Rest controller) or the specified action from the route (if the controller is an Action controller).

This above convention is defined within watson.framework.config.views, however this can be overridden if required.

*The views settings within watson.framework.config*

.. code-block:: python

    views = {
        'default_format': 'html',
        'renderers': {
            'default': {
                'name': 'jinja2_renderer',
                'config': {
                    'extension': 'html',
                    'paths': [os.path.join(os.getcwd(), 'views')],
                    'packages': [('my.application', 'views')]
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

Jinja2 Helper Filters and Functions
-----------------------------------

There are several Jinja2 helpers available:

.. function:: url(route_name, host=None, scheme=None, **kwargs)

   Convenience method to access the router from within a Jinja2 template.

   :param route_name: the route to build the url for
   :param host: the host name to add to the url
   :param scheme: the scheme to use
   :param kwargs: additional params to be used in the route
   :rtype: string matching the url

.. function:: merge_query_string(obj, values)

   Merges an existing dict of query string values and updates the values.

   :param obj: the original dict

.. function:: config()

   Convenience method to retrieve the configuration of the application.

.. function:: get_request()

   Convenience method to retrieve the current request.

.. _Jinja2: http://jinja.pocoo.org/docs/
