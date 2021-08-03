Apache + mod-wsgi configuration
===============================

An example Apache2 vhost configuration follows::

    WSGIDaemonProcess sdg-<target> threads=5 maximum-requests=1000 user=<user> group=staff
    WSGIRestrictStdout Off

    <VirtualHost *:80>
        ServerName my.domain.name

        ErrorLog "/srv/sites/sdg/log/apache2/error.log"
        CustomLog "/srv/sites/sdg/log/apache2/access.log" common

        WSGIProcessGroup sdg-<target>

        Alias /media "/srv/sites/sdg/media/"
        Alias /static "/srv/sites/sdg/static/"

        WSGIScriptAlias / "/srv/sites/sdg/src/sdg/wsgi/wsgi_<target>.py"
    </VirtualHost>


Nginx + uwsgi + supervisor configuration
========================================

Supervisor/uwsgi:
-----------------

.. code::

    [program:uwsgi-sdg-<target>]
    user = <user>
    command = /srv/sites/sdg/env/bin/uwsgi --socket 127.0.0.1:8001 --wsgi-file /srv/sites/sdg/src/sdg/wsgi/wsgi_<target>.py
    home = /srv/sites/sdg/env
    master = true
    processes = 8
    harakiri = 600
    autostart = true
    autorestart = true
    stderr_logfile = /srv/sites/sdg/log/uwsgi_err.log
    stdout_logfile = /srv/sites/sdg/log/uwsgi_out.log
    stopsignal = QUIT

Nginx
-----

.. code::

    upstream django_sdg_<target> {
      ip_hash;
      server 127.0.0.1:8001;
    }

    server {
      listen :80;
      server_name  my.domain.name;

      access_log /srv/sites/sdg/log/nginx-access.log;
      error_log /srv/sites/sdg/log/nginx-error.log;

      location /500.html {
        root /srv/sites/sdg/src/sdg/templates/;
      }
      error_page 500 502 503 504 /500.html;

      location /static/ {
        alias /srv/sites/sdg/static/;
        expires 30d;
      }

      location /media/ {
        alias /srv/sites/sdg/media/;
        expires 30d;
      }

      location / {
        uwsgi_pass django_sdg_<target>;
      }
    }
