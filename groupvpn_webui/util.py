from random import randrange
from string import ascii_lowercase

from django.conf import settings
from django import forms
from django.core.exceptions import ValidationError
from django.db import models
import ipaddress

DEFAULTS = {
    'arg': 'blarg',
    'GROUPVPN_XMPP_HOST': 'localhost',
    'GROUPVPN_MAX_MACHINES': 10, # Note: Don't make this too large, because
                                 # groupvpn-config currently has to make
                                 # n^2 calls to ejabberdctl
    'GROUPVPN_IP_PREFIX_MINIMUM_LENGTH': 16,
    'GROUPVPN_CONFIG_ARGS': ['groupvpn-config', '--password-length', '30',
                             '--zip']
}

class IPNetworkField(models.CharField):
    __metaclass__ = models.SubfieldBase
    description = "A network of IP addresses"

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 50
        super(IPNetworkField, self).__init__(*args, **kwargs)
        # Remove the MaxLength validator that CharField.__init__ adds
        self.validators.pop()
        self.validators.append(validate_ip_network_prefix_length)

    def formfield(self, **kwargs):
        defaults = {'form_class': IPNetworkFormField}
        defaults.update(kwargs)
        return super(IPNetworkField, self).formfield(**defaults)

    def get_prep_value(self, value):
        return str(value)

    def to_python(self, value):
        if isinstance(value, (ipaddress.IPv4Network, ipaddress.IPv6Network)):
            return value
        return ipaddress.ip_network(value)

class IPNetworkFormField(forms.CharField):
    def clean(self, value):
        try:
            ipn = ipaddress.ip_network(value)
        except ValueError as e:
            raise forms.ValidationError(e)
        return ipn

def get_setting(name):
    if name not in defaults:
        raise NameError("%s is not a valid setting name" % name)
    try:
        return getattr(settings, name)
    except AttributeError:
        return DEFAULTS[name]

def random_string_maker(length):
    def random_string():
        return u''.join(unichr(randrange(0xFFFF)) for _ in range(length))
    return random_string

def validate_ip_network_prefix_length(value):
    min_len = get_setting('GROUPVPN_IP_PREFIX_MINIMUM_LENGTH')
    if value.prefixlen < min_len:
        raise ValidationError(u"Prefix length must be %d or higher" % min_len)
