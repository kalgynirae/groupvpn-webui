from __future__ import absolute_import
import json
import math
import random
import re
import string
import tempfile
import zipfile

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.core.validators import RegexValidator
from django.db import models
import ipaddress

from .util import IPNetworkField, random_string_maker

PASSWORD_CHARS = string.ascii_lowercase + string.digits
PASSWORD_LENGTH = 30
XMPP_HOST = 'localhost:9000'

class Configuration(models.Model):
    owner = models.ForeignKey(User, null=True)
    group_name = models.CharField(
        max_length=100, primary_key=True,
        validators=[RegexValidator(r'^\w+$', "Must match the regex '\w+'")])
    machine_count = models.IntegerField("number of machines")
    ip_network = IPNetworkField(
        default="172.31.0.0/24",
        help_text="Enter the network base address followed by either a "
                  "netmask or a prefix length.")
    end_to_end_security = models.BooleanField(blank=True)
    random_seed = models.CharField(
        max_length=20,
        default=random_string_maker(20))

    def __unicode__(self):
        return "<Configuration: '%s' by %s>" % (self.group_name, self.owner)

    def clean(self):
        # We usually can't use the network address or the broadcast address
        unusable_addresses = 2
        address_count = self.ip_network.num_addresses - unusable_addresses
        if self.machine_count > address_count:
            raise ValidationError(
                "IP network contains insufficient usable addresses (%(c)s).",
                params={'c': address_count})

    def get_absolute_url(self):
        return reverse('view_edit_configuration', args=[self.pk])

    def generate_configs(self):
        rnd = random.Random()
        rnd.seed(self.random_seed)
        digits = int(math.log10(max(1, self.machine_count - 1))) + 1
        username_template = "%s_{:0%d}" % (self.group_name, digits)
        ips = iter(self.ip_network.hosts())
        configs = []
        for n in range(1, self.machine_count + 1):
            username = username_template.format(n)
            password = ''.join(rnd.choice(PASSWORD_CHARS)
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
        # Assemble the zip file and return a response object
        filename = self.group_name + '.zip'
        with tempfile.TemporaryFile() as file:
            with zipfile.ZipFile(file, 'w') as z:
                for config in self.generate_configs():
                    z.writestr(config['filename'], config['data'])
            file.seek(0)
            return file.read(), filename

    def setup_ejabberd(self):
        pass
