from setuptools import setup

setup(
    name="groupvpn-webui",
    packages=["groupvpn_webui"],
    install_requires=[
        "Django >=1.6.3, <1.7",
        "ipaddress ==1.0.6",
    ],
)
