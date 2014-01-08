from __future__ import absolute_import
import json
import math
import random
import re
import subprocess
import tempfile
import zipfile

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.core.validators import RegexValidator
from django.db import models
import ipaddress

from .util import IPNetworkField, random_string_maker

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

    def get_zipped_configs(self):
        filename = self.group_name + '.zip'
        args = ['gvpn-config.py', self.group_name, str(self.machine_count),
                str(self.ip_network), self.xmpp_host, '--password-length',
                settings.GROUPVPN_PASSWORD_LENGTH, '--seed', self.random_seed]
        output = subprocess.check_output(args)
        return output, filename
