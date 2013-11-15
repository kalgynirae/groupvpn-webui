import json
import math
import random
import re
import string

from flask import Flask, redirect, render_template, request, url_for
import ipaddress
import wtforms as w

PASSWORD_CHARS = string.ascii_lowercase + string.digits
PASSWORD_LENGTH = 30

class IPNetworkField(w.Field):
    widget = w.widgets.TextInput()

    def __init__(self, label=None, validators=None, **kwargs):
        super(IPNetworkField, self).__init__(label, validators, **kwargs)

    def _value(self):
        if self.raw_data:
            return self.raw_data[0]
        elif self.data is not None:
            return str(self.data)
        else:
            return ''

    def process_formdata(self, valuelist):
        if valuelist:
            try:
                self.data = ipaddress.ip_network(valuelist[0])
            except ValueError as e:
                self.data = None
                raise ValueError(e)

class ConfigurationForm(w.Form):
    group_name = w.TextField("Group name", [w.validators.DataRequired()])
    xmpp_host = w.TextField("XMPP host", [w.validators.DataRequired()])
    machine_count = w.IntegerField(
        "Number of machines", [w.validators.NumberRange(min=2)])
    ip_network = IPNetworkField(
        "IP network", default=ipaddress.ip_network(u"192.168.0.0/24"),
        description="Enter the network base address followed by either a "
                    "netmask or a prefix length.")
    end_to_end_security = w.BooleanField("End-to-end security")

    def validate(self):
        return (super(ConfigurationForm, self).validate() and
                self.validate_enough_addresses())

    def validate_enough_addresses(self):
        available_addresses = self.ip_network.data.num_addresses
        if available_addresses >= self.machine_count.data:
            return True
        else:
            self.ip_network.errors.append("Network only contains {} addresses"
                                          "".format(available_addresses))
            return False

def make_configs(group_name, xmpp_host, ip_network,
                 machine_count, end_to_end_security):
    max_digits = int(math.log10(machine_count - 1)) + 1
    username_template = "{}{{:0{}}}".format(group_name, max_digits)
    ips = iter(ip_network.hosts())
    configs = []
    for n in range(1, machine_count + 1):
        username = re.sub(r'\W+', '_', username_template.format(n).lower())
        password = ''.join(random.choice(PASSWORD_CHARS)
                           for _ in range(PASSWORD_LENGTH))
        data = {
            'xmpp_username': username,
            'xmpp_password': password,
            'xmpp_host': xmpp_host,
            'ip': str(next(ips)),
        }
        configs.append({'filename': "{}.json".format(username),
                        'data': json.dumps(data, indent=4) + '\n'})
    return configs

app = Flask(__name__)
app.jinja_env.trim_blocks = True
app.jinja_env.keep_trailing_newline = True

@app.route('/', methods=['GET'])
def configurate():
    form = ConfigurationForm(request.args)
    if request.args and form.validate():
        configs = make_configs(form.group_name.data, form.xmpp_host.data,
                               form.ip_network.data,
                               form.machine_count.data,
                               form.end_to_end_security.data)
    else:
        configs = None
    return render_template('configuration.html', form=form, configs=configs,
                           action_url=url_for('configurate'))

if __name__ == '__main__':
    app.run(debug=True)
