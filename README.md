A web frontend for configuring ejabberd and generating configuration
files for SocialVPN

Set-up
======

Obtain the source and set up a virtualenv:

    $ git clone https://github.com/kalgynirae/groupvpn-webui.git
    $ cd groupvpn-webui
    $ virtualenv .

Install dependencies:

    $ bin/pip install -r requirements.txt

Change the secret key in the django settings file:

    $ vim project/settings.py

Create the database:

    $ bin/python manage.py syncdb
