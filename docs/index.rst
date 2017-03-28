.. Watson - Framework documentation master file, created by
   sphinx-quickstart on Fri Jan 17 14:49:48 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. role:: python(code)
   :language: python

Watson - A Python 3 Web Framework
==============================================

    It's elementary my dear Watson

|Build Status| |Coverage Status| |Version| |Downloads| |Licence|

Watson is an easy to use framework designed to get out of your way and
let you code your application rather than spend time wrangling with the
framework. It follows the convention over configuration ideal, although
the convention can be overriden if required. Out of the box it comes
with a standard set of defaults to allow you to get coding straight
away!

Requirements
------------

Watson is designed for Python 3.3 and up.

Dependencies
------------

Watson currently requires the following modules to work out of the box:

-  `Jinja2`_
    - For view templating

These will be installed automatically if you have installed Watson via
pip.

Optional Dependencies
---------------------

Some packages within Watson require third party packages to run
correctly, these include:

-  `Memcached`_
    - pip package: python3-memcached

-  `Redis`_
    - pip package: redis

Notes about these dependencies can be found within the relevant
documentation in the :ref:`reference_library`.

Installation
------------

``pip install watson-framework``

Testing
-------

Watson can be tested with py.test. Simply activate your virtualenv and run :python:`python setup.py test`.

Benchmarks
----------

Using falcon-bench, Watson received the following requests per second (Django and Flask supplied for comparative purposes).

1. watson.........11,920 req/sec or 83.89 μs/req  (3x)
2. django..........7,696 req/sec or 129.94 μs/req (2x)
3. flask...........4,281 req/sec or 233.58 μs/req (1x)

Contributing
------------

If you would like to contribute to Watson, please feel free to issue a
pull request via Github with the associated tests for your code. Your
name will be added to the AUTHORS file under contributors.

Table of Contents
-----------------

.. include:: toc.rst.inc

.. _Jinja2: http://jinja.pocoo.org/docs/
.. _Memcached: http://pypi.python.org/pypi/python3-memcached/
.. _Redis: https://github.com/andymccurdy/redis-py

.. |Build Status| image:: https://api.travis-ci.org/watsonpy/watson-framework.png?branch=master
   :target: https://travis-ci.org/watsonpy/watson-framework
.. |Coverage Status| image:: https://coveralls.io/repos/watsonpy/watson-framework/badge.png
   :target: https://coveralls.io/r/watsonpy/watson-framework
.. |Version| image:: https://pypip.in/v/watson-framework/badge.png
   :target: https://pypi.python.org/pypi/watson-framework/
.. |Downloads| image:: https://pypip.in/d/watson-framework/badge.png
   :target: https://pypi.python.org/pypi/watson-framework/
.. |Licence| image:: https://pypip.in/license/watson-framework/badge.png
   :target: https://pypi.python.org/pypi/watson-framework/
