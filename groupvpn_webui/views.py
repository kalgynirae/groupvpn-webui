import json
import math
import random
import re
import string
import tempfile
import zipfile

from flask import Flask, redirect, render_template, request, Response, url_for
import ipaddress
import wtforms as w

GROUP_SALT_CHARS = string.ascii_lowercase + string.digits
GROUP_SALT_LENGTH = 5
PASSWORD_CHARS = GROUP_SALT_CHARS
PASSWORD_LENGTH = 30
XMPP_HOST = 'localhost:9000'

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
    machine_count = w.IntegerField(
        "Number of machines", [w.validators.NumberRange(min=2)])
    ip_network = IPNetworkField(
        "IP network", default=ipaddress.ip_network(u"192.168.0.0/24"),
        description="Enter the network base address followed by either a "
                    "netmask or a prefix length.")
    end_to_end_security = w.BooleanField("End-to-end security", default=True)

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

def generate_configs(group_name, xmpp_host, ip_network, machine_count,
                     end_to_end_security):
    digits = int(math.log10(machine_count - 1)) + 1
    username_template = "%s_{:0%d}" % (group_name, digits)
    ips = iter(ip_network.hosts())
    configs = []
    for n in range(1, machine_count + 1):
        username = username_template.format(n)
        password = ''.join(random.choice(PASSWORD_CHARS)
                           for _ in range(PASSWORD_LENGTH))
        data = {
            'ip': str(next(ips)),
            'xmpp_username': username,
            'xmpp_password': password,
            'xmpp_host': xmpp_host,
            'end_to_end_security': end_to_end_security,
        }
        configs.append({'filename': "{}.json".format(username),
                        'data': json.dumps(data, indent=4) + '\n'})
    return configs

def generate_configs_and_zip(form):
    # Sanitize the group name and add some salt
    salt = ''.join(random.choice(GROUP_SALT_CHARS)
                   for _ in range(GROUP_SALT_LENGTH))
    sanitized = re.sub(r'\W+', '_', form.group_name.data.lower())
    group_name = '%s_%s' % (sanitized, salt)

    configs = generate_configs(group_name, XMPP_HOST,
                               form.ip_network.data,
                               form.machine_count.data,
                               form.end_to_end_security.data)

    # Assemble the zip file and return a Flask response
    filename = group_name + '.zip'
    with tempfile.TemporaryFile() as file:
        with zipfile.ZipFile(file, 'w') as z:
            for config in configs:
                z.writestr(config['filename'], config['data'])
        file.seek(0)
        r = Response(file.read(), status=200, mimetype='application/zip')
        r.headers['Content-Disposition'] = 'attachment; filename=%s' % filename
        return r

app = Flask(__name__)
app.jinja_env.trim_blocks = True
app.jinja_env.keep_trailing_newline = True

@app.route('/', methods=['GET', 'POST'])
def configurate():
    form = ConfigurationForm(request.form)
    if request.method == 'POST' and form.validate():
        return generate_configs_and_zip(form)
    return render_template('configuration.html', form=form,
                           action_url=url_for('configurate'), method='post')

if __name__ == '__main__':
    app.run(debug=True)
