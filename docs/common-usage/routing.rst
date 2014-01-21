.. _common_usage_routing:

Routing
=======

Routing is an important part of Watson as it ties a request directly to a controller (and subsequently a view). Routes are generally defined within the ``project/app_name/config/routes.py`` file, which is then imported into your applications configuration file.

The anatomy of a route
----------------------

Routes within Watson consist of several key parts, and at a bare minimum must contain the following:

1. A name to identify it
2. A path to match against
3. A controller to execute

A route is defined within a simple dict() in the following way:

.. code-block:: python

    routes = {
        'route_name': {
            'path': '/',
            'options': {
                'controller': 'package.module.Controller'
            }
        }
    }

.. attention::
    0.2.6 introduced a breaking change that separated options from defaults

When a user hits / in their browser, then a new instance of package.module.Controller will be instantiated, and the relevant view will be rendered to the browser.

Ordering of routes
------------------

The ordering of routes is important, however as dicts are unordered you must supply a priority within the route.

.. code-block:: python

    routes = {
        'route_name': {
            'path': '/resource',
        },
        'route_name_post': {
            'path': '/resource',
            'accepts': ('POST',)
            'priority': 1
        }
    }

When /resource is sent to the browser, the response from route_name will always be returned first, regardless of the http request method being used. However by adding priority to route_name_post, if the POST request method is used, then route_name_posts contents will be returned.

Creating complex routes
-----------------------

There are times when you may wish to only allow access to a particular route via a single http request method, or perhaps only if a specific format is requested.

Accepting specific request methods
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Simply add a list/tuple of valid http request methods to the 'accepts' key on the route.

.. code-block:: python

    routes = {
        'route_name': {
            'path': '/resource',
            'accepts': ('GET', 'POST')
            'options': {
                'controller': 'package.module.Controller'
            }
        }
    }

+---------------------+--------+---------+
| Url                 | Verb   | Matched |
+=====================+========+=========+
| /resource           | GET    | Yes     |
+---------------------+--------+---------+
| /resource           | PUT    | No      |
+---------------------+--------+---------+

Subdomains
^^^^^^^^^^

Simply add the subdomain to the 'subdomain' key on the route (it also accepts a tuple of subdomains).

.. code-block:: python

    routes = {
        'route_name': {
            'path': '/resource',
            'subdomain': 'clients'
        }
    }

+---------------------+------------------+---------+
| Url                 | Host             | Matched |
+=====================+==================+=========+
| /resource           | www.site.com     | No      |
+---------------------+------------------+---------+
| /resource/123       | clients.site.com | Yes     |
+---------------------+------------------+---------+

Creating segment driven routes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A segment route is basically a route that contains a series of placeholder values. These can be mandatory, or optional depending on how they are configured. Any segments will be sent as keyword arguments to the controllers that they execute, though they can be ignored.

*Mandatory segment*

.. code-block:: python

    routes = {
        'route_name': {
            'path': '/resource/:id',
        }
    }

+---------------------+---------+-----+
| Url                 | Matched | id  |
+=====================+=========+=====+
| /resource           | No      |     |
+---------------------+---------+-----+
| /resource/123       | Yes     | 123 |
+---------------------+---------+-----+

*Optional segment*

.. code-block:: python

    routes = {
        'route_name': {
            'path': '/resource/:id[/:resource_action]',
            'defaults': {
                'resource_action': 'view'
            }
        }
    }

+---------------------+---------+-----+-----------------+
| Url                 | Matched | id  | resource_action |
+=====================+=========+=====+=================+
| /resource           | No      |     |                 |
+---------------------+---------+-----+-----------------+
| /resource/123       | Yes     | 123 | view            |
+---------------------+---------+-----+-----------------+
| /resource/123/edit  | Yes     | 123 | edit            |
+---------------------+---------+-----+-----------------+

*Optional segment with required values*

.. code-block:: python

    routes = {
        'route_name': {
            'path': '/resource/:id[/:resource_action]',
            'defaults': {
                'resource_action': 'view'
            },
            'requires': {
                'resource_action': 'view|edit|delete'
            }
        }
    }

+---------------------+---------+-----+-----------------+
| Url                 | Matched | id  | resource_action |
+=====================+=========+=====+=================+
| /resource           | No      |     |                 |
+---------------------+---------+-----+-----------------+
| /resource/123       | Yes     | 123 | view            |
+---------------------+---------+-----+-----------------+
| /resource/123/edit  | Yes     | 123 | edit            |
+---------------------+---------+-----+-----------------+
| /resource/123/show  | No      |     |                 |
+---------------------+---------+-----+-----------------+

Generating urls from routes
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Routes can be converted back to specific urls by using the assemble method on either the router object itself, or the assemble method on the route. Most of the time a url needs to be generated within the controller action, and as such the controller class provides a url() method which takes the same arguments as assemble(). Any keyword arguments that are passed to these functions replace any segments within the route path.

*Route configuration (leaving out default key for berevity)*

.. code-block:: python

    routes = {
        'route_name': {
            'path': '/resource/:id',
        }
    }

*In a controller within your application*

.. code-block:: python

    class Resource(controllers.Rest):
        def GET(self):
            resource = self.url(id=3)  # /resource/3
            # could also be represented as self.get('router').assemble(id=3)
