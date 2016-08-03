Watson-Framework
================

::

    It's elementary my dear Watson

Watson is an easy to use framework designed to get out of your way and
let you code your application rather than wrangle with the framework.

For full documentation please see `Read The
Docs <http://watson-framework.readthedocs.org/>`__.

Build Status
^^^^^^^^^^^^

|Build Status| |Coverage Status| |Version|

Installation
------------

``pip install watson-framework``

Dependencies
------------

-  watson-cache
-  watson-common
-  watson-console
-  watson-di
-  watson-dev
-  watson-events
-  watson-filter
-  watson-form
-  watson-html
-  watson-http
-  watson-routing
-  watson-validators

Benchmarks
----------

Using falcon-bench, Watson received the following requests per second (Django and Flask supplied for comparative purposes).

1. watson.........11,920 req/sec or 83.89 ms/req  (3x)
2. django..........7,696 req/sec or 129.94 ms/req (2x)
3. flask...........4,281 req/sec or 233.58 ms/req (1x)

.. |Build Status| image:: https://img.shields.io/travis/watsonpy/watson-framework.svg?maxAge=2592000
   :target: https://travis-ci.org/watsonpy/watson-framework
.. |Coverage Status| image:: https://img.shields.io/coveralls/watsonpy/watson-framework.svg?maxAge=2592000
   :target: https://coveralls.io/r/watsonpy/watson-framework
.. |Version| image:: https://img.shields.io/pypi/v/watson-framework.svg?maxAge=2592000
   :target: https://pypi.python.org/pypi/watson-framework/
