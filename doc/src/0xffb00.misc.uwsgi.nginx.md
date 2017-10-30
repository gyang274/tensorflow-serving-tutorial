## uWSGI + Nginx

### uWSGI Application Service

#### Overview

- concept: `the web client <-> the web server <-> the socket <-> uwsgi <-> python`

#### Install uWSGI
 
```
$ sudo apt-get install build-essential python-dev 

# in case the distro is built in module with plugins must install separately

$ sudo apt-get install uwsgi-core uwsgi-plugin-python
```

- //src/misc/test.py

```
def application(env, start_response):
    start_response('200 OK', [('Content-Type','text/html')])
    # return [b"Hello World"] # python3
    return ["Hello World"] # python2
```

```
$ uwsgi --http :8000 --wsgi-file test.py

# in case the distro is built in module with plugins must loaded separately
$ uwsgi --plugin http,python --http :8000 --wsgi-file test.py
$ uwsgi --plugin python --http-socket :8000 --wsgi-file test.py

# the web client <-> uwsgi <-> python works
```

#### Create uWSGI Configuration File

- `//src/misc/test.ini`

```
[uwsgi]
project = test

# user and group
uid = www-data
gid = www-data

# project base directory
base = <git-repo-base>/src/misc

# project wsgi application
chdir = %(base)
module = test:application

plugins = python

# python home directory
pyhome = /usr
enable-threads = true

# route the static
# route = /static/(.*) static:%(base)/dist/$1

# master and worker
master = true
processes = 5

# socket
socket = /run/uwsgi/%(project).sock
chown-socket = %(uid):%(gid)
chmod-socket = 666

vaccum = true

die-on-term = true
```

#### Inspect uWSGI Configuration File

```
$ sudo mkdir -p /run/uwsgi

$ sudo chown www-data:www-data /run/uwsgi

$ sudo chmod 0666 /run/uwsgi
 
$ sudo uwsgi --http-socket :8000 --ini </path/to/test.ini>

$ sudo uwsgi --http-socket :8000 --ini test.ini

# python threads support enabled (disabled default)
$ sudo uwsgi --http-socket :8000 --ini test.ini --enable-threads
```

#### Add uWSGI into `systemd` 

- create symbolic link in system to configuration file

```
$ sudo ls /etc/uwsgi
> apps-available/ apps-enabled/

# in case no apps-available and apps-enabled dir seen
# $ sudo mkdir -p /etc/uwsgi/apps-available/ /etc/uwsgi/apps-enabled/

# $ sudo ln -s $PWD/test.ini /etc/uwsgi/apps-available/test.ini

$ sudo ln -s $PWD/test.ini /etc/uwsgi/apps-enabled/test.ini
```

- create a `systemd daemon` for uWSGI

```
$ sudo touch /etc/systemd/system/uwsgi.service
```
- `/etc/systemd/system/uwsgi.service`

```
[Unit]
Description=uWSGI Emperor service

[Service]
ExecStartPre=/bin/bash -c 'mkdir -p /run/uwsgi; chown www-data:www-data /run/uwsgi'
ExecStart=/usr/bin/uwsgi --emperor /etc/uwsgi/apps-enabled
Restart=always
KillSignal=SIGQUIT
Type=notify
NotifyAccess=all

[Install]
WantedBy=multi-user.target
```

- start `uwsgi.service` via `systemd`

```
$ sudo systemctl daemon-reload

$ sudo systemctl start uwsgi.service

$ sudo systemctl status uwsgi.service

$ sudo systemctl restart uwsgi.service
```

### Nginx Web Service

#### Install Nginx

```
$ sudo apt-get install nginx

$ which nginx
> /usr/sbin/nginx

$ nginx -v
> nginx version: nginx/1.10.3 (Ubuntu)
```

#### Start Nginx Web Service (default)

```
$ sudo systemctl start nginx.service

$ sudo systemctl status nginx.service

$ sudo systemctl restart nginx.service

# the web client <-> the web server works 
```

#### Inspect Nginx Web Service (default)

```
$ curl 127.0.0.1:80
...
<!DOCTYPE html>
<html>
<head>
<title>Welcome to nginx!</title>
<style>
    body {
        width: 35em;
        margin: 0 auto;
        font-family: Tahoma, Verdana, Arial, sans-serif;
    }
</style>
</head>
<body>
<h1>Welcome to nginx!</h1>
<p>If you see this page, the nginx web server is successfully installed and
working. Further configuration is required.</p>

<p>For online documentation and support please refer to
<a href="http://nginx.org/">nginx.org</a>.<br/>
Commercial support is available at
<a href="http://nginx.com/">nginx.com</a>.</p>

<p><em>Thank you for using nginx.</em></p>
</body>
</html>
...
```

#### Configure Nginx to Proxy to uWSGI

- remove default site configuration file

```
# remove default configuration in /etc/nginx/sites-enabled/default
# but keep one in /etc/nginx/sites-available/default for reference

$ sudo unlink /etc/nginx/sites-enabled/default

$ sudo systemctl restart nginx.service

$ curl 127.0.0.1:80
> curl: (7) Failed to connect to 127.0.0.1 port 80: Connection refused
```

- create customized site configuration file

```
$ sudo touch /etc/nginx/sites-available/ygsite

# /etc/nginx/sites-available/ygsite
... 
server {
  listen 8000;
  server_name 127.0.0.1;
  location = /favicon.ico { access_log off; log_not_found off; }
  
  # static 
  # location /static/ {
  #   root /srv/site/ygsite/dist;
  # }
  # uwsgi-apps
  location / {
    uwsgi_pass  unix:/run/uwsgi/test.sock;
    include     uwsgi_params;
  }
}
...
```

- create symbolic link into site-enabled

```
$ sudo ln -s /etc/nginx/sites-available/ygsite /etc/nginx/sites-enabled

$ sudo unlink /etc/nginx/sites-enabled/ygsite

$ sudo ln -s /etc/nginx/sites-available/ygsite /etc/nginx/sites-enabled
```

- check the configuration and run

```
$ sudo nginx -t

$ sudo systemctl restart nginx.service

$ sudo uwsgi --http-socket :8000 --ini /etc/uwsgi/apps-enabled/test.ini

$ sudo systemctl restart uwsgi.service
```

