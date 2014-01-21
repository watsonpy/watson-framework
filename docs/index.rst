.. Watson - Framework documentation master file, created by
   sphinx-quickstart on Fri Jan 17 14:49:48 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. role:: python(code)
   :language: python

Watson - A Python 3 Web Framework
==============================================

    It's elementary my dear Watson

+-----------+------------------+---------------------+
| Branch    | Status           | Coverage            |
+===========+==================+=====================+
| Master    | |Build StatusM|  | |Coverage Status|   |
+-----------+------------------+---------------------+
| Develop   | |Build StatusD|  |                     |
+-----------+------------------+---------------------+

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

Watson currently requires the following modules to work out of box:

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

Notes about these dependencies can be found within the relevant
documentation in the :ref:`reference_library`.

Testing
-------

Watson can be tested with py.test. Simply activate your virtualenv and run :python:`python setup.py test`.

Contributing
------------

If you would like to contribute to Watson, please feel free to issue a
pull request via Github with the associated tests for your code. Your
name will be added to the AUTHORS file under contributors.

.. _Jinja2: http://jinja.pocoo.org/docs/
.. _Memcached: http://pypi.python.org/pypi/python3-memcached/
.. _Redis: https://github.com/andymccurdy/redis-py

.. |Coverage Status| image:: https://coveralls.io/repos/bespohk/watson-framework/badge.png
   :target: https://coveralls.io/r/bespohk/watson-framework
.. |Build StatusD| image:: https://api.travis-ci.org/bespohk/watson-framework.png?branch=develop
   :target: https://travis-ci.org/bespohk/watson-framework
.. |Build StatusM| image:: https://api.travis-ci.org/bespohk/watson-framework.png?branch=master
   :target: https://travis-ci.org/bespohk/watson-framework
.. |Pypi| image:: https://pypip.in/v/watson-framework/badge.png
   :target: https://crate.io/packages/watson-framework/


Table of Contents
-----------------

.. include:: toc.rst.inc
