import itertools
import json
import math
import random
import string

from flask import Flask, redirect, render_template, request, url_for
from wtforms import Form, BooleanField, IntegerField, TextField, validators

PASSWORD_CHARS = string.ascii_lowercase + string.digits
PASSWORD_LENGTH = 30

class ConfigurationForm(Form):
    group_name = TextField("Group name", [validators.DataRequired()])
    xmpp_host = TextField("XMPP host", [validators.DataRequired()])
    ip_base = TextField("IP base", [validators.IPAddress()])
    ip_netmask = TextField("IP netmask", [validators.IPAddress()])
    machine_count = IntegerField("Number of machines",
                                 [validators.NumberRange(min=0)])
    end_to_end_security = BooleanField("End-to-end security")

app = Flask(__name__)
app.jinja_env.trim_blocks = True
app.jinja_env.keep_trailing_newline = True

@app.route('/', methods=['GET'])
def home():
    return redirect(url_for('configurate'))

@app.route('/style.css', methods=['GET'])
def stylesheet():
    return redirect(url_for('configurate'))

@app.route('/configurate', methods=['GET', 'POST'])
def configurate():
    form = ConfigurationForm(request.form)
    if request.method == 'POST' and form.validate():
        configs = make_configs(form.group_name.data, form.xmpp_host.data,
                               form.ip_base.data, form.ip_netmask.data,
                               form.machine_count.data,
                               form.end_to_end_security.data)
        return render_template('success.html', form=form, configs=configs)
    return render_template('configuration.html', form=form,
                           post_url=url_for('configurate'))

def make_configs(group_name, xmpp_host, ip_base, ip_netmask, machine_count,
                 end_to_end_security):
    username_template = "{}{{:0{}}}".format(group_name,
                                            int(math.log10(machine_count)) + 1)
    ips = generate_ips(ip_base, ip_netmask)
    configs = []
    for i in range(machine_count):
        username = username_template.format(i)
        password = ''.join(random.choice(PASSWORD_CHARS)
                           for _ in range(PASSWORD_LENGTH))
        data = {
            'xmpp_username': username,
            'xmpp_password': password,
            'xmpp_host': xmpp_host,
            'ip': next(ips),
            'ip_netmask': ip_netmask,
        }
        configs.append({'filename': "{}.json".format(username),
                        'data': json.dumps(data, indent=4)})
    return configs

def generate_ips(base, mask):
    # TODO: Do this better.
    a, b, c, d = map(int, base.split('.'))
    for n in itertools.count():
        yield '{}.{}.{}.{}'.format(a, b, c, d + n)

if __name__ == '__main__':
    app.run(debug=True)
