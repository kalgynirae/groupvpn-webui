import json
import math
import random
import re
import string
import tempfile
import zipfile

from django import forms
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import models
import ipaddress

GROUP_SALT_CHARS = string.ascii_lowercase + string.digits
GROUP_SALT_LENGTH = 0
PASSWORD_CHARS = GROUP_SALT_CHARS
PASSWORD_LENGTH = 30
XMPP_HOST = 'localhost:9000'

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

    def generate_configs(self):
        digits = int(math.log10(max(1, self.machine_count - 1))) + 1
        username_template = "%s_{:0%d}" % (self.group_name, digits)
        ips = iter(self.ip_network.hosts())
        configs = []
        for n in range(1, self.machine_count + 1):
            username = username_template.format(n)
            password = ''.join(random.choice(PASSWORD_CHARS)
                               for _ in range(PASSWORD_LENGTH))
            data = {
                'ip': str(next(ips)),
                'xmpp_username': username,
                'xmpp_password': password,
                'xmpp_host': XMPP_HOST,
                'end_to_end_security': self.end_to_end_security,
            }
            configs.append({'filename': "{}.json".format(username),
                            'data': json.dumps(data, indent=4) + '\n'})
        return configs

    def get_zipped_configs(self):
        # Sanitize the group name and add some salt
        salt = ''.join(random.choice(GROUP_SALT_CHARS)
                       for _ in range(GROUP_SALT_LENGTH))
        sanitized = re.sub(r'\W+', '_', self.group_name.lower())
        group_name = '%s_%s' % (sanitized, salt) if salt else sanitized

        configs = self.generate_configs()

        # Assemble the zip file and return a response object
        filename = group_name + '.zip'
        with tempfile.TemporaryFile() as file:
            with zipfile.ZipFile(file, 'w') as z:
                for config in configs:
                    z.writestr(config['filename'], config['data'])
            file.seek(0)
            return file.read(), filename

class ConfigurationForm(forms.ModelForm):
    class Meta:
        model = Configuration
        fields = ['group_name', 'machine_count', 'ip_network',
                  'end_to_end_security']

class LimitedConfigurationForm(ConfigurationForm):
    machine_count = forms.IntegerField(
        max_value=2,
        error_messages={'max_value': "Must be less than or equal to 2 (log in "
                                     "to allow higher)."})
