#!/bin/bash

master=saltspark1
minions=(saltspark1, saltspark2, saltspark3)

# parse input arguments
usage() { echo "Usage: $0 [-u <string> softlayer username] [-k <string> softlayer api key]" 1>&2; exit 1; }

while getopts ":u:k:" opt; do
  case $opt in
    u) user="$OPTARG"
    ;;
    k) key="$OPTARG"
    ;;
    *) usage
    ;;
  esac
done
shift $((OPTIND-1))

if [ -z "${user}" ] || [ -z "${key}" ]; then
    usage
fi

cat > /etc/salt/cloud.providers.d/softlayer.conf << EOF
sl:
  minion:
    master: $public_ip
  user: $user
  apikey: $key
  provider: softlayer
  script: bootstrap-salt
  script_args: -Z
  delete_sshkeys: True
  display_ssh_output: False
  wait_for_ip_timeout: 1800
  ssh_connect_timeout: 1200
  wait_for_fun_timeout: 1200
EOF

cat /etc/salt/cloud.providers.d/softlayer.conf

cat > /etc/salt/cloud.profiles.d/softlayer.conf << EOF
sl_centos7_small:
  provider: sl
  image: CENTOS_7_64
  cpu_number: 1
  ram: 1024
  disk_size: 25
  local_disk: True
  hourly_billing: True
  domain: w251final.net
  location: dal05
EOF

# create map file used to start multiple instances at once
cat /dev/null >| /etc/salt/cloud.map
for minion in ${minions[@]}; do
    echo "  - ${minion}" >> /etc/salt/cloud.map
done
salt-cloud -m /etc/salt/cloud.map -P -y

# passwordless ssh
ssh-keygen -t rsa -N "" -f ~/.ssh/id_rsa

# get private ips
salt '*' network.interface_ip eth0 | sed 'N;s/\n\ \+/ /' > /etc/salt/roster
