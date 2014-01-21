.. _advanced_topics_deployments:

Deployments
===========

.. note::
    In all of the examples below, ``site.com`` should be replaced with your own site.

uWSGI
-----


.. code-block:: yaml

    uwsgi:
        master: true
        processes: 1
        vaccum: true
        chmod-socket: 666
        uid: www-data
        gid: www-data
        socket: /tmp/site.com.sock
        chdir: /var/www/site.com/site
        logoto: /var/www/site.com/data/logs/error_log
        home: /var/virtualenvs/3.3
        pythonpath: /var/www/site.com
        module: app
        touch-reload: /var/www/site.com/site/app.py


nginx
-----

.. parsed-literal::

    server {
        listen 80;
        server_name site.com;
        root /var/www/site.com/public;

        location /css {
            access_log off;
        }

        location /js {
            access_log off;
        }

        location /img {
            access_log off;
        }

        location /fonts {
            access_log off;
        }

        location / {
            include uwsgi_params;
            uwsgi_pass unix:/tmp/site.com.sock;
        }
    }
