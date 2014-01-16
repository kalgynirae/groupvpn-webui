A tool for generating configurations for GroupVPN and ejabberd. Also
includes a Django-based web interface.

Dependencies
============

*   The Python2 versions of `virtualenv` and `pip` (packages `python-pip` and
    `python-virtualenv` on Debian)

*   `ejabberd` server already running, with `ejabberdctl` available.

Set-up
======

Obtain the source and set up a virtualenv:

    $ git clone https://github.com/kalgynirae/groupvpn-webui.git
    $ cd groupvpn-webui
    $ virtualenv .env

Install dependencies to the virtualenv:

    $ .env/bin/pip install -e .

Using the command-line tool
=============================

View help message:

    $ .env/bin/gvpn-config -h

Generate configuration files for 10 machines:

    $ .env/bin/gvpn-config testgroup localhost:1337 10 > configs.zip

By default `ejabberdctl` commands are printed but not run. The
`--configure` flag runs them:

    $ .env/bin/gvpn-config --configure testgroup localhost:1337 10 > configs.zip

Django set-up
=============

Change the secret key and disable `DEBUG` in the django settings file:

    $ vim project/settings.py

Create the database:

    $ .env/bin/manage.py syncdb
