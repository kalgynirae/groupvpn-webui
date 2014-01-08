#!/usr/bin/python2
import argparse
import io
import json
import math
import random
import string
import subprocess
import sys
import zipfile

import ipaddress

PASSWORD_CHARS = string.ascii_lowercase + string.digits

def ip_network(s):
    return ipaddress.ip_network(s.decode())
parser = argparse.ArgumentParser(description='Configure GroupVPN')
parser.add_argument('--version', action='version', version='1')
parser.add_argument('group_name')
parser.add_argument('xmpp_host')
parser.add_argument('machine_count', type=int)
parser.add_argument('--ip-network', type=ip_network, required=False,
                    default=ipaddress.ip_network(u'172.31.0.0/24'))
parser.add_argument('--password-length', default=30, type=int,
                    help="length of generated XMPP passwords (default 30)")
parser.add_argument('--no-security', dest='security', action='store_false',
                    help="Don't use end-to-end security")
parser.add_argument('--no-xmpp-setup', dest='xmpp_setup', action='store_false',
                    help="Don't set up XMPP accounts")
parser.add_argument('--no-zip', dest='zip', action='store_false',
                    help="Don't pack output in a zip archive")
parser.add_argument('--seed', help="seed for the random number generator")
args = parser.parse_args()

if args.seed:
    random.seed(args.seed)

digits = int(math.log10(max(1, args.machine_count - 1))) + 1
ip_network = ipaddress.ip_network(args.ip_network)
username_template = "%s_{:0%d}" % (args.group_name, digits)

configs = []
for n, ip in zip(range(1, args.machine_count + 1), ip_network.hosts()):
    username = username_template.format(n)
    password = ''.join(random.choice(PASSWORD_CHARS)
                       for _ in range(args.password_length))
    data = {
        'ip': str(ip),
        'xmpp_username': username,
        'xmpp_password': password,
        'xmpp_host': args.xmpp_host,
        'end_to_end_security': args.security,
    }
    configs.append({'filename': "%s.json" % username,
                    'data': json.dumps(data, indent=4) + '\n'})

if args.xmpp_setup:
    for config in configs:
        args = ['ejabberdctl', 'register', username, args.xmpp_host, password]
        subprocess.check_call(args)
    # TODO: make friendships between users

with io.BytesIO() as b:
    if args.zip:
        with zipfile.ZipFile(b, 'w') as z:
            for config in configs:
                z.writestr(config['filename'], config['data'])
    else:
        for config in configs:
            b.write(config['data'])
    b.seek(0)
    print b.read()
