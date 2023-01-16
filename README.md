![build](https://github.com/HolgerGraef/MSM/actions/workflows/ci.yml/badge.svg)
![coverage](https://raw.githubusercontent.com/HolgerGraef/MSM/python-coverage-comment-action-data/badge.svg)
![flake8](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/HolgerGraef/1cfaee423c85504cd204cf4649e2cf29/raw/flake8-badge.json)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Documentation Status](https://readthedocs.org/projects/msm/badge/?version=latest)](https://msm.readthedocs.io/en/latest/?badge=latest) [![Join the chat at https://gitter.im/Mercury-Sample-Manager/community](https://badges.gitter.im/Mercury-Sample-Manager/community.svg)](https://gitter.im/Mercury-Sample-Manager/community?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

# Mercury Sample Manager

This is Mercury Sample Manager, a sample management tool that enables researchers
to keep track of their samples from any PC in a laboratory. The programme is a Flask-based web service that runs on a
central server on the local network of your research institute and that can be accessed from all other computers on the
same network using the normal web browser (should be a recent browser though).

## Disclaimer

The developers take no responsibility for the loss or theft of data managed by this software.
The software sends anonymous usage statistics to the developers, including the software version, the number of users,
samples and actions stored in the database, the server uptime and the used/available disk space.

## Coding style

Install the developer requirements for MSM:

    make install-dependencies

In order to auto-correct coding style, use:

    make black

In order to run this as a pre-commit hook, use:

    pre-commit install

## Installation of development server

This programme should work an almost any platform (Linux, Windows, MacOS), but I only provide the installation
instructions for Linux. Seeing that you should install it on a server, I suppose Linux is the target OS in most
cases anyways.

You should have python 3.x and python3-venv installed on your system. Using a virtual environment is not absolutely necessary, but I recommend it. You can now create a folder somewhere
and clone the git repository:

    $ git clone git@github.com:HolgerGraef/MSM.git

Now you enter this directory and you create a virtual environment for python - and activate it:

    $ cd MSM
    $ python3 -m venv venv
    $ . venv/bin/activate
    $ pip install --upgrade pip

Finally, all that remains to do is to install the required python packages:

    $ pip install -r requirements.txt
    
Now you have to initialise the database by running:

    $ python manage.py db upgrade
    
Note that, if you want to initialise the database for deployment (i.e. in the "production" configuration), you should
first set up the FLASK_CONFIG variable accordingly:

    $ export FLASK_CONFIG=production && python manage.py db upgrade

This will also create the admin user that you will use for your first login (admin@admin.com, password is admin).

You can update the details (user name, email and password) of the administrator in the "Profile" section (you will find the corresponding button on the top right after logging in). Also remember to set up an email account in the corresponding subsection of the "Settings" page.

You can set up a site name for usage statistics by writing it into a file "usage_stats_site" in the MSM folder.

You can start the development server by simply executing:

    $ make run-no-docker

## Using GitHub deploy keys

As long as this is a private repository, access can be granted using deploy keys. You can generate a public/private key
pair by executing `ssh-keygen -t rsa -C "[email address]"` and copy the content of the corresponding public key file to
the "Deploy Keys" section in the repository's settings page on GitHub. Note that if the key is not the default key
(`~/.ssh/id_rsa`), you need to set up a config file for ssh (`~/.ssh/config`), e.g.:

    Host msm.github.com
      HostName github.com
      User git
      IdentityFile /home/[user]/.ssh/msm_rsa
      IdentitiesOnly yes
      
In this case, we defined a new hostname for github.com (msm.github.com) for the key file `msm_rsa` and the above
`git clone` command has to be modified as follows:

    git clone git@msm.github.com:HolgerGraef/MSM.git

## Development with docker

Set up some tools:

1. install Docker, see https://docs.docker.com/engine/install/ubuntu/
2. install pywatchman:
    - sudo apt install watchman
    - `pip install -i https://test.pypi.org/simple/ pywatchman==1.4.2.dev1` (c.f. https://github.com/facebook/watchman/issues/970)


Build and run:

    make build-dev
    make run-dev

## Running with docker

docker compose -f docker/docker-compose.yml build web
docker compose -f docker/docker-compose.yml up web

## Deployment with gunicorn and nginx

Carry out the steps described above in order to set up the development server. Then configure gunicorn autostart
by setting up a corresponding autostart file. This is explained below either for upstart or for systemd.

Please note that the app should be executed in the HTTP root, bugs should be expected when you install MSM in a
subfolder.

Note the use of the `--preload` option for gunicorn in the following, which ensures that the thread for reporting
usage statistics is only started once (before the worker processes are forked). Also note that you can test the
multiprocessing behaviour in your development environment by running e.g.:

    gunicorn [--preload] --workers 4 --bind 127.0.0.1 manage:app 

## For upstart

Create the file /etc/init/msm.conf and copy the following code into it:
 
    description "Gunicorn application server running Mercury Sample Manager"
    
    start on runlevel [2345]
    stop on runlevel [!2345]
    
    respawn
    setuid [user name]
    setgid www-data
    
    env FLASK_CONFIG=production
    env PATH=[path]/MSM/venv/bin:/usr/bin
    chdir [path]/MSM
    exec gunicorn --preload --workers 4 --bind unix:msm.sock -m 007 manage:app

Where you will have to replace [user name] by your user name and [path] by the path where you installed the programme. The second path (/usr/bin) is where you should have installed the git executable.

## For systemd

Create the file /lib/systemd/system/msm.service and copy the following code into it:

    [Unit]
    Description=Gunicorn application server running Mercury Sample Manager

    [Service]
    Restart=on-failure
    User=[user name]
    Group=www-data

    Environment=FLASK_CONFIG=production
    Environment=PATH=[path]/MSM/venv/bin:/usr/bin
    WorkingDirectory=[path]/MSM
    ExecStart=[path]/MSM/venv/bin/gunicorn --preload --workers 4 --bind unix:msm.sock -m 007 manage:app

    [Install]
    WantedBy=multi-user.target

Where you will have to replace [user name] by your user name and [path] by the path where you installed the programme. The second path (/usr/bin) is where you should have installed the git executable.

Note that for the execution of gunicorn, the group has to be set to `www-data` so that the `msm.sock` file is accessible
for the nginx server (this also applies to the upstart configuration above).

Now activate autostart:

    sudo systemctl enable msm

## in both cases, continue here:

Now install nginx:

    $ sudo apt-get install nginx

Create an SSL certificate and key in the following folder:

    $ sudo mkdir /etc/nginx/ssl
    $ cd /etc/nginx/ssl

In order to create SSL certificate and key follow the steps given in https://www.digitalocean.com/community/tutorials/how-to-create-a-ssl-certificate-on-nginx-for-ubuntu-12-04

You then want to configure your nginx server. Create a file "msm" in /etc/nginx/sites-available and copy the following content into it:

    server {
        listen 80;
        server_name localhost;
        rewrite        ^ https://$server_name$request_uri? permanent;
    }
    
    
    # HTTPS server
    
    server {
        listen 443;
        server_name localhost;
    
        ssl on;
        ssl_certificate /etc/nginx/ssl/server.crt;
        ssl_certificate_key /etc/nginx/ssl/server.key;
    
        location / {
        include proxy_params;
          proxy_pass http://unix:[path]/MSM/msm.sock;
        }
    }

Where - again - you have to replace [path] by the path to the application's directory. Then create a symbolic link to
this file in /etc/nginx/sites-enabled and delete the default entry:

    $ sudo ln -s /etc/nginx/sites-available/msm /etc/nginx/sites-enabled
    $ sudo rm /etc/nginx/sites-enabled/default

If you want your server to support large file uploads, you have to change /etc/nginx/nginx.conf and add the following
line to the http context to increase the size limit (in this example 5 Megabytes):

    # set client body size to 5M #
    client_max_body_size 5M;

You can now start your server by executing:
 
    $ sudo start msm
    $ sudo service nginx restart
    
If you use upstart, for systemd type:

    $ sudo systemctl start msm
    $ sudo systemctl restart nginx

The server will now automatically - i.e. also after a reboot - be available on localhost.

More details: https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-14-04
