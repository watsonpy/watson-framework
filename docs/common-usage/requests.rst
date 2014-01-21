.. _common_usage_requests:

Requests
========

For the following we're assuming that all requests come through the route:

.. code-block:: python

    routes = {
        'example': {
            'path': '/path',
            'options': { 'controller': 'Public' }
        }
    }

Accessing request variables
---------------------------

Accessing GET variables
^^^^^^^^^^^^^^^^^^^^^^^

Assuming the following http request:

.. parsed-literal::

    /path/?query=string&value=something


.. code-block:: python

    class Public(controllers.Rest):
        def GET(self):
            query = self.request.get['query']  # string

Accessing POST variables
^^^^^^^^^^^^^^^^^^^^^^^^

Assuming the following http request:

.. parsed-literal::

    /path

With the following key/value pairs of data being posted: data: something

.. code-block:: python

    class Public(controllers.Rest):
        def GET(self):
            data = self.request.post['data']  # something

Accessing FILE variables
^^^^^^^^^^^^^^^^^^^^^^^^

Assuming the following http request:

.. parsed-literal::

    /path

With

.. code-block:: html

    <input type="file" name="a_file" />

being posted.

.. code-block:: python

    class Public(controllers.Rest):
        def GET(self):
            file = self.request.files['a_file']  # cgi.FieldStorage

Accessing cookies
^^^^^^^^^^^^^^^^^

Assuming the following http request:

.. parsed-literal::

    /path

.. code-block:: python

    class Public(controllers.Rest):
        def GET(self):
            cookies = self.request.cookies  # CookieDict

Accessing session data
^^^^^^^^^^^^^^^^^^^^^^

Assuming the following http request:

.. parsed-literal::

    /path

With the following data being stored in the session: data: value

.. code-block:: python

    class Public(controllers.Rest):
        def GET(self):
            session = self.request.session
            session_data = session['data']  # value
            session.id  # id of the session

Accessing SERVER variables (environ variables)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    class Public(controllers.Rest):
        def GET(self):
            server = self.request.server['PATH_INFO']  # /path
