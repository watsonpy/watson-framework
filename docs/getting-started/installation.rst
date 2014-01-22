Installation
============


All stable versions of Watson are available via `pip`_ and can be
installed using the following command ``pip install watson-framework``
via your CLI of choice.

Watson is maintained at `Github`_, and can be used to get the latest
development version of the code if required.

Setting up a virtualenv
-----------------------

We recommend creating a standalone environment for each new project you
work on to isolate any dependencies that it may need. To do so enter the
following commands in your terminal:

.. code-block:: bash

   >>> pyvenv /where_you_want_to_store_venv
   >>> source /where_you_want_to_store_venv/bin/activate

Verifying the installation
--------------------------

To ensure that Watson has been installed correctly, launch ``python``
from your CLI and then enter the following:

.. code-block:: python

   >>> import watson
   >>> print(watson.__version__)
   >>> # latest watson version will be printed here

Once you've got Watson installed, head on over to the :ref:`your_first_application` area to learn how to create your first web application.

.. _pip: https://pypi.python.org/pypi/pip
.. _Github: http://github.com/watsonpy/watson-framework
