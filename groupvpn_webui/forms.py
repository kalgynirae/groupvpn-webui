from __future__ import absolute_import

from django import forms

from .models import Configuration

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
