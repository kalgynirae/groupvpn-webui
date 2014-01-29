A tool for generating configurations for GroupVPN and ejabberd. Also
includes a Django-based web interface.

Dependencies
------------

*   The Python2 versions of **virtualenv** and **pip** (packages
    `python-pip` and `python-virtualenv` on Debian)

*   **ejabberd** server already running, with `ejabberdctl` available.

Installation
------------

Obtain the source and set up a virtualenv with the needed dependencies:

    $ git clone https://github.com/kalgynirae/groupvpn-webui.git
    $ cd groupvpn-webui
    $ virtualenv .env
    $ .env/bin/pip install -e .

This will install the `gvpn-config` tool and the django `manage.py`
script to the `.env/bin/` directory, so you can run them like this:

    $ .env/bin/gvpn-config
    $ .env/bin/manage.py

Using the `gvpn-config` tool
-----------------------------

The `gvpn-config` tool generates GroupVPN configurations for you. It can
output a zip archive containing the configuration files, and it can set
up the needed Jabber accounts and relationships for you (but for this to
work it needs to be able to use the `ejabberdctl` command).

View the help message:

    $ .env/bin/gvpn-config --help

Generate configuration files for 10 machines:

    $ .env/bin/gvpn-config testgroup localhost:1337 10 --zip > configs.zip

By default, `ejabberdctl` commands are printed but not run. Use the
`--configure` flag to actually run them:

    $ .env/bin/gvpn-config --configure testgroup localhost:1337 10 --zip > configs.zip

Passwords are randomly generated, so if you need to generate the same
passwords on multiple runs of the tool, you can pass a string to be used
as a random seed using the `--seed` option:

    $ .env/bin/gvpn-config testgroup localhost 10 --seed asdfghjkl

Django set-up
-------------

Change the secret key and disable `DEBUG` in the django settings file:

    $ vim project/settings.py

Create the database:

    $ .env/bin/manage.py syncdb
