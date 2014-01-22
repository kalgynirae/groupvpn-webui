A tool for generating configurations for GroupVPN and ejabberd. Also
includes a Django-based web interface.

Dependencies
============

*   The Python2 versions of **virtualenv** and **pip** (packages `python-pip` and
    `python-virtualenv` on Debian)

*   **ejabberd** server already running, with `ejabberdctl` available.

Installation
============

Obtain the source and set up a virtualenv:

    $ git clone https://github.com/kalgynirae/groupvpn-webui.git
    $ cd groupvpn-webui
    $ virtualenv .env

Install dependencies to the virtualenv:

    $ .env/bin/pip install -e .

Using the `gvpn-config` tool
=============================

[TODO: general description]

View help message:

    $ .env/bin/gvpn-config -h

Generate configuration files for 10 machines:

    $ .env/bin/gvpn-config testgroup localhost:1337 10 --zip > configs.zip

By default `ejabberdctl` commands are printed but not run. Use the
`--configure` flag to actually run them:

    $ .env/bin/gvpn-config --configure testgroup localhost:1337 10 --zip > configs.zip

Passwords are randomly generated, so if you need to generate the same
passwords on multiple runs of the tool, you can pass a string to be used
as a random seed using the `--seed` option:

    $ .env/bin/gvpn-config testgroup localhost 10 --seed kajfslafkslalfj

Django set-up
=============

Change the secret key and disable `DEBUG` in the django settings file:

    $ vim project/settings.py

Create the database:

    $ .env/bin/manage.py syncdb
