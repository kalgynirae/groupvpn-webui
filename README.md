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
    $ virtualenv .

Install dependencies to the virtualenv:

    $ bin/pip install -r requirements.txt

Using the command-line tool
=============================

View help message:

    $ bin/python gvpn-config.py -h

Generate configuration files and configure ejabberd:

    $ bin/python gvpn-config.py --configure testgroup localhost:1337 10 > configs.zip

By default `ejabberdctl` commands are printed but not run. The
`--configure` flag runs them.

Django set-up
=============

Change the secret key and disable `DEBUG` in the django settings file:

    $ vim project/settings.py

Create the database:

    $ bin/python manage.py syncdb
