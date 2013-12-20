from django import forms
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import models
import ipaddress

class IPNetworkField(models.Field):
    __metaclass__ = models.SubfieldBase
    description = "A network of IP addresses"

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 50
        super(IPNetworkField, self).__init__(*args, **kwargs)

    def get_prep_value(self, value):
        return str(value)

    def to_python(self, value):
        if isinstance(value, (ipaddress.IPv4Network, ipaddress.IPv6Network)):
            return value
        try:
            ipn = ipaddress.ip_network(value)
        except ValueError as e:
            raise ValidationError(e)
        return ipn

class Configuration(models.Model):
    group_name = models.CharField(max_length=100)
    machine_count = models.IntegerField("number of machines")
    ip_network = IPNetworkField(
        default="172.31.0.0/24",
        help_text="Enter the network base address followed by either a "
                  "netmask or a prefix length.")
    end_to_end_security = models.BooleanField(blank=True)

    def __unicode__(self):
        return "<Configuration: '%s'>" % self.group_name

    def clean(self):
        # We usually can't use the network address or the broadcast address
        unusable_addresses = 2
        address_count = self.ip_network.num_addresses - unusable_addresses
        if self.machine_count > address_count:
            raise ValidationError(
                "IP network contains insufficient usable addresses (%(c)s).",
                params={'c': address_count})

    def get_absolute_url(self):
        return reverse('edit', args=[str(self.id)])

class ConfigurationForm(forms.ModelForm):
    model = Configuration
    fields = ['group_name', 'machine_count', 'ip_network',
              'end_to_end_security']
