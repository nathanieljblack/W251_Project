#!/usr/bin/env python

import SoftLayer.API
import sys
import json
import time
 
api_username = "XXX"
api_key = "XXX"
ssh_id = "XXX"

with open('./start_cluster/config.json') as json_data:
    config = json.load(json_data)
    json_data.close()

num = int(sys.argv[1])
 
client = SoftLayer.Client (
    username=api_username,
    api_key=api_key
)

def wait_for_instance(id):
    provisionDate = ''
    vg = ''
    while provisionDate == '':
        vglist = client['Account'].getVirtualGuests()
        vg = [v for v in vglist if v['id'] == id][0]
        provisionDate = vg['provisionDate']
    if vg != '':
        return vg['primaryIpAddress'], vg['primaryBackendIpAddress']
    return '', ''

ids = []
names = []
publicIPs = []
privateIPs = []

for i in range(num):
    name = 'sp' + str(i+1)
    newCCI = config
    newCCI['hostname'] = name
    newCCI['sshKeys'] = [{"id": ssh_id}]

    result = client['Virtual_Guest'].createObject(newCCI)
    names.append(name)
    ids.append(result['id'])

    #publicIP, privateIP = wait_for_instance(result['id'])
    #publicIPs.append(publicIP)
    #privateIPs.append(privateIP)

    time.sleep(5)

for i in range(len(ids)):
    publicIP, privateIP = wait_for_instance(ids[i])
    publicIPs.append(publicIP)
    privateIPs.append(privateIP)

with open('./local/etc_hosts', 'w') as hosts_file:
    hosts_file.write("127.0.0.1 localhost\n")
    for i in range(len(names)):
        hosts_file.write("{0} {1}\n".format(privateIPs[i], names[i]))

with open('./hosts', 'w') as hosts_file:
    hosts_file.write('[local]\n')
    hosts_file.write('localhost ansible_connection=local\n')
    hosts_file.write('\n[cluster]\n')
    for i in range(len(publicIPs)):
        hosts_file.write('{} ansible_connection=ssh ansible_ssh_user=root\n'.format(publicIPs[i]))

    hosts_file.write('\n[master]\n')
    hosts_file.write('{} ansible_connection=ssh ansible_ssh_user=root\n'.format(publicIPs[0]))

with open('./hadoop/master.conf', 'w') as f:
    f.write(names[0])

with open('./hadoop/slaves.conf', 'w') as f:
    for i in range(len(publicIPs)):
        f.write('{}\n'.format(names[i]))
