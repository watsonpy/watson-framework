.. _your_first_application:


Your First Application
======================

Directory Structure
-------------------

Watson has a preferred directory structure for it's applications which can be created automatically by the ``watson-console.py project new [project name] [app name]`` command.

.. code-block:: bash

    /project_root
        /app_name
            /config
                config.py
                dev.py.dist
                prod.py.dist
                routes.py
            /controllers
            /views
                /layouts
            app.py
        /data
            /cache
            /logs
            /uploads
        /public
            /css
            /img
            /js
        /tests
        console.py


.. tip::
    For example **watson-console.py project new sample.com.local sample** creates a new project named sample.com.local and an application package named sample

The application will be created within the current working directory, unless you override it with the ``-d DIR`` option.

Once the structure has been created, you can use ``./console.py`` to perform related console commands from within the application, for example: ``./console.py project routes`` to display a list of routes for the application.

Configuration
-------------

By creating your project using the **project new** command Watson will generate 3 configuration files for your application as well as a route file.

1. config.py
2. dev.py.dist
3. prod.py.dist
4. routes.py

config.py is the basic configuration to get your application up and running locally and is identical to dev.py.dist. By default dev.py.dist will enable profiling and debugging of the application. If you have retrieved the application from a VCS then you would make a copy of dev.py.dist with the name config.py and modify the settings within there.

*app/config/config.py*

.. code-block:: python

    from project.config.routes import routes

    debug = {
        'enabled': True,
    }

When deploying to a production environment you would make a copy of prod.py.dist and name it config.py to load the relevant production settings.

The dist files are designed to maintain a consistent configuration when an application is being worked on by multiple developers. We recommend adding [app_name]/config/config.py to your .gitignore file to prevent your personal configuration from being used by another developer.

routes.py contains all the routes associated with the application. For more detail on how to define routes, please see the :ref:`key_concepts_mvc` Key Concept area.

*app/config/routes.py*

.. code-block:: python

    routes = {
        'index': {
            'path': '/',
            'defaults': {'controller': 'project.controllers.Index'}
        }
    }

Putting it all together
-----------------------

Most likely you'll want to develop locally first and then deploy to a production environment later. Watson comes packaged with a command to run a local development server which will automatically reload when changes are saved. To run the server simply change to the project directory and run ``./console.py dev runserver`` and then visit http://127.0.0.1:8000 in your favorite browser where you'll be greeted with a page saying welcome to Watson.

A initial controller is created for you in app_name/controllers/index.py which will response to a request for / in your browser (from the above routes.py definition)

*app/controllers/index.py*

.. code-block:: python

    from watson.framework import controllers, __version__

    class Index(controllers.Rest):
        def GET(self):
            return 'Welcome to Watson v{0}!'.format(__version__)

Being a Rest controller any request will be routed to the instance method matching the HTTP_REQUEST_METHOD environ variable from the associated request. One of the benefits of using a Rest controller is that you no longer need to check the request method to determine how you should respond.

An alternative would be to use an Action controller instead. This would be represented in the following way:

.. code-block:: python

    from watson.framework import controllers, __version__

    class Index(controllers.Action):
        def index_action(self):
            return 'Welcome to Watson v{0}!'.format(__version__)

All Action controller methods are suffixed with _action. For a more indepth look at what functions a controller can perform, check out the :ref:`common_usage` area for controllers. For a general overview of how controllers are used within Watson, check out the :ref:`key_concepts_mvc` Key Concept area.

The presentation layer (or view) is matched based on lowercased versions of the the class name and action of the controller. For the above request the following view is rendered:

*app/views/index/get.html*

.. code-block:: html

    <!DOCTYPE html>
    <html>
        <head>
            <title>Welcome to Watson!</title>
        </head>
        <body>
            <h1>{{ content }}</h1>
            <p>You are now on your way to creating your first application using Watson.</p>
            <p>Read more about Watson in <a href="http://github.com/watsonpy/watson-framework">the documentation.</a>
        </body>
    </html>

For more information on views, check out the :ref:`key_concepts_mvc` Key Concept area.

You will also want to make sure that you unit test your application, and you can do that by running ``./console.py project test``. A simple unit test is already included when the **project new** command is run. It is designed to fail so make sure you go in and make the required changes for it to pass!

All tests are located under the tests directory. For example the demo unit test is located at tests/[app name]/controllers/test_index.py.

Watson supports both nose and `py.test`_ for use with the ``project test`` command and one of these is required to run application test suites.

.. _py.test: http://pytest.org/latest/
