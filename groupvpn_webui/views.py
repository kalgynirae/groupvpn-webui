import json
import math
import random
import re
import string
import tempfile
import zipfile

from django.http import HttpResponse
from django.shortcuts import render
import ipaddress

from .models import ConfigurationForm

GROUP_SALT_CHARS = string.ascii_lowercase + string.digits
GROUP_SALT_LENGTH = 5
PASSWORD_CHARS = GROUP_SALT_CHARS
PASSWORD_LENGTH = 30
XMPP_HOST = 'localhost:9000'

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
        response = HttpResponse(file.read(), content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename=%s' % filename
        return response

def configure(request):
    form = ConfigurationForm(request.POST)
    if request.method == 'POST' and form.validate():
        return generate_configs_and_zip(form)
    context = {'form': form, 'method': 'post'}
    return render(request, 'groupvpn_webui/configuration.html', context)
