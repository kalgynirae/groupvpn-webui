A Django app providing a web interface for creating GroupVPN
configurations.

Dependencies
------------

*   The Python2 versions of **virtualenv** and **pip** (packages
    `python-pip` and `python-virtualenv` on Debian)

*   **ejabberd** server already running, with `ejabberdctl` available.

*   The [groupvpn-config] script

*   A web server to run the django application in such a way that the
    application can run `groupvpn-config` with correct permissions

*   Django and the Python 2 backport of Python 3's `ipaddress` module
    (these can be installed easily using `pip` with the included
    `setup.py` file)

Installation
------------

1.  Install dependencies. This repository contains a `setup.py` script
    that will install the groupvpn_webui application, Django, and the
    needed ipaddress module. I haven't yet figured out how to run Django
    properly out of a virtualenv installation, but your mileage may
    vary.

2.  Start a new Django project (or modify an existing one) and add
    `groupvpn_webui` to the INSTALLED_APPS. Configure settings in the
    project's `settings.py` file if desired (for a list of settings, see
    the defaults in `util.py`). In particular, if `groupvpn-config` has
    to be invoked in a special manner, modify `GROUPVPN_CONFIG_ARGS`.

3.  Configure your web server to serve the Django project, and make sure
    everything works!

[groupvpn-config]: https://github.com/kalgynirae/groupvpn-config
