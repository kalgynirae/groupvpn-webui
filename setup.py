from setuptools import setup
import os.path

setup(
    name="gvpn",
    packages=['groupvpn_webui', 'project'],
    install_requires=[
        "Django >=1.5, <1.6",
        "django-registration >=1.0, <1.1",
        "django-registration-email >=0.7.1, <0.8",
        "ipaddress >=1.0.6, <1.1",
    ],
    scripts=["gvpn-config", "manage.py"],
)
