from setuptools import setup

setup(
    name="groupvpn-webui",
    packages=["groupvpn_webui", "django_project"],
    install_requires=[
        "Django >=1.6.3, <1.7",
        "django-registration >=1.0, <1.1",
        "django-registration-email >=0.7.1, <0.8",
        "ipaddress ==1.0.6",
    ],
    scripts=["manage.py"],
)
