from random import randrange
from string import ascii_lowercase

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
import ipaddress

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

def random_string_maker(length):
    def random_string():
        return u''.join(unichr(randrange(0xFFFF)) for _ in range(length))
    return random_string

def validate_ip_network_prefix_length(value):
    if value.prefixlen < settings.GROUPVPN_IP_PREFIX_MINIMUM_LENGTH:
        raise ValidationError(u"Prefix length must be %d or higher" %
                              settings.GROUPVPN_IP_PREFIX_MINIMUM_LENGTH)

