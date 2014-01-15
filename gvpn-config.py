"""Generate configuration files for GroupVPN.

This program does two things: it runs the necessary `ejabberdctl` commands to
set up users for each machine, and it prints to stdout out a zip archive
containing a configuration file for each machine.

If any error is encountered during the `ejabberdctl` calls, this program will
exit immediately.
"""
from __future__ import print_function
import argparse
import io
import itertools
import json
import math
import random
import string
import subprocess
import sys
import zipfile

import ipaddress

PASSWORD_CHARS = string.ascii_lowercase + string.digits

def print_and_call(command):
    print(('' if args.configure else '#') + ' '.join(command), file=sys.stderr)
    if args.configure:
        try:
            subprocess.check_call(command)
        except subprocess.CalledProcessError as e:
            print(e, file=sys.stderr)
            print("Exiting after ejabberdctl error.", file=sys.stderr)
            sys.exit(42)

def ip_network_from_str(s):
    # The ipaddress module only excepts unicode objects, so we have to decode
    # the string that comes in on the command line.
    return ipaddress.ip_network(s.decode())

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('group_name')
parser.add_argument('xmpp_host')
parser.add_argument('machine_count', type=int)
parser.add_argument('--configure', action='store_true',
                    help="Run ejabberdctl commands (default: just print them)")
parser.add_argument('--ip-network', type=ip_network_from_str, required=False,
                    default=ipaddress.ip_network(u'172.31.0.0/24'),
                    help="IP network for the group (default: 172.31.0.0/24)")
parser.add_argument('--no-security', dest='security', action='store_false',
                    help="Don't configure for end-to-end security")
parser.add_argument('--no-zip', dest='zip', action='store_false',
                    help="Output plain text instead of a zip archive")
parser.add_argument('--password-length', default=30, type=int,
                    help="length of generated XMPP passwords (default: 30)")
parser.add_argument('--seed',
                    help="Seed the random number generator")
parser.add_argument('--version', action='version', version='1')
args = parser.parse_args()

if args.seed:
    random.seed(args.seed)

digits = int(math.log10(max(1, args.machine_count - 1))) + 1
ip_network = ipaddress.ip_network(args.ip_network)
username_template = "%s_{:0%d}" % (args.group_name, digits)

# Generate configuration data
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
    configs.append({'filename': "%s.json" % username, 'data': data})

# Register users with ejabberd
for config in configs:
    command = ['ejabberdctl', 'register', config['data']['xmpp_username'],
               args.xmpp_host, config['data']['xmpp_password']]
    print_and_call(command)

# Set up friendships between users
for c1, c2 in itertools.permutations(configs, 2):
    usernames = [c['data']['xmpp_username'] for c in [c1, c2]]
    nick = '%s-%s' % tuple(usernames)
    group = 'groupvpn'
    subscription = 'both'
    command = ['ejabberdctl', 'add-rosteritem',
               usernames[0], args.xmpp_host,
               usernames[1], args.xmpp_host,
               nick, group, subscription]
    print_and_call(command)

with io.BytesIO() as b:
    if args.zip:
        with zipfile.ZipFile(b, 'w') as z:
            for config in configs:
                z.writestr(config['filename'],
                           json.dumps(config['data'], indent=4) + '\n')
    else:
        for config in configs:
            b.write(json.dumps(config['data'], indent=4) + '\n')
    b.seek(0)
    print(b.read())
