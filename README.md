A Django-based web interface for creating GroupVPN configurations.

Dependencies
------------

*   The Python2 versions of **virtualenv** and **pip** (packages
    `python-pip` and `python-virtualenv` on Debian)

*   **ejabberd** server already running, with `ejabberdctl` available.

*   The [groupvpn-config] script

*   A web server to run the django application in such a way that the
    application can run `sudo groupvpn-config`

Installation
------------

Obtain the source and set up a virtualenv with the needed dependencies:

    $ git clone https://github.com/kalgynirae/groupvpn-webui.git
    $ cd groupvpn-webui
    $ virtualenv env
    $ env/bin/pip install -e .

This will install the django `manage.py` script to the `.env/bin/`
directory, so you can run it like this:

    $ env/bin/manage.py

Django set-up
-------------

Change the secret key in the django settings file:

    $ vim django_project/local_config.py

Create the database:

    $ env/bin/manage.py syncdb

[groupvpn-config]: https://github.com/kalgynirae/groupvpn-config
