#!/usr/bin/env python
# Copyright 2019 Kevin McJunkin
# License: Apache

import json
import os
import subprocess
import platform

# Find distro
distro = platform.dist()
version = distro[1]
distro = distro[0]



# Mount config drive and grab network json
os.system('mount /dev/xvdd /mnt/')
with open('/mnt/openstack/latest/network_data.json', 'r') as f:
    network_dict = json.load(f)


# Grab our needed information for eth0
public_net = '00000000-0000-0000-0000-000000000000'
for device in network_dict['networks']:
    if device['network_id'] == public_net:
        if device['type'] == 'ipv4':
            ip = device['ip_address']
            mask = device['netmask']
            for route in device['routes']:
                gateway = route['gateway']

nameservers = []
for service in network_dict['services']:
    nameservers.append(service['address'])


# Interface file strings
cent = '''
# Automatically generated, do not edit

# Label public
BOOTPROTO=static
DEVICE=eth0
IPADDR=%s
NETMASK=%s
GATEWAY=%s
DNS1=%s
DNS2=%s
ONBOOT=yes
NM_CONTROLLED=no
'''

ubuntu = '''
# The loopback network interface
auto lo
iface lo inet loopback

# Label public

auto eth0
iface eth0 inet static
	address %s
	netmask %s
	gateway %s
	dns-nameservers %s %s\n'''


# Inject our vars into an interface file string
ubuntu = ubuntu % (ip, mask, gateway, nameservers[0], nameservers[1])
cent = cent % (ip, mask, gateway, nameservers[0], nameservers[1])


# Replace stale interface file with our updated one
if distro == 'centos':
    try:
        os.remove('/etc/sysconfig/network-scripts/ifcfg-eth0')
    except FileNotFoundError:
        pass
    f = open('/etc/sysconfig/network-scripts/ifcfg-eth0', 'w+')
    f.write(cent)
    f.close()

if distro == 'Ubuntu':
    try:
        os.remove('/etc/network/interfaces')
    except FileNotFoundError:
        pass
    f = open('/etc/network/interfaces', 'w+')
    f.write(ubuntu)
    f.close()


# Bounce interface
os.system('ifdown eth0 && ifup eth0')


# Pull down and install an older version of nova-agent
hash = 'e584a326fabd876c3b87-5cc4f7b75bc093abc6d4ecc36a7bc696'
domain = '.r2.cf1.rackcdn.com/'
tarball = 'nova-agent-Linux-i686-0.0.1.37.tar.gz'
endpoint = 'http://' + hash + domain + tarball

os.system('curl ' + endpoint + '>' + '/tmp/' + tarball)
os.system('tar -C /tmp/ -xvf /tmp/' + tarball)
subprocess.call('/tmp/installer.sh')


# Start and enable nova-agent
if distro == 'centos':
    if float(version) < 7:
        os.system('service nova-agent start')
        os.system('chkconfig nova-agent on')
    elif float(version) > 7:
        os.system('systemctl start nova-agent')
        os.system('systemctl enable nova-agent')

if distro == 'Ubuntu':
    if float(version) < 16:
        os.system('service nova-agent start')
    elif float(version) > 16:
        os.system('systemctl start nova-agent')
        os.system('systemctl enable nova-agent')
