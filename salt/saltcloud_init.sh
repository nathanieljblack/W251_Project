#!/bin/bash

# provision a master
#slcli vs create -d dal05 --os CENTOS_7_64 --cpu 1 --memory 1024 --hostname saltmaster --domain w251final.net --key mids

# to do:
#   [x] parameterize user:key
#   [] display private ip
#   [] run provision command and wait for curl to return results
#       e.g., while ! ping -c1 www.google.com &>/dev/null; do :; done
#       from http://serverfault.com/questions/42021/how-to-ping-in-linux-until-host-is-known
#   [] remove need to paste root pwd twice
#   [] parameterize hostname

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

# get details
vs_hostname="saltmaster2"
masterdetails=$(curl 'https://'"${user}"':'"${key}"'@api.softlayer.com/rest/v3/SoftLayer_Account/VirtualGuests.json?objectMask=id;fullyQualifiedDomainName;hostname;domain;primaryIpAddress;operatingSystem.passwords' | jq -r '.[] | select (.hostname == "'"${vs_hostname}"'") |{fullyQualifiedDomainName,id,root_password: .operatingSystem.passwords[] | select(.username == "root").password,primaryIpAddress}')
root_pwd=$(echo $masterdetails | jq -r '.["root_password"]')
public_ip=$(echo $masterdetails | jq -r '.["primaryIpAddress"]')

# add saltmaster to known hosts to bypass y/n prompt
#ssh-keyscan $public_ip >> ~/.ssh/known_hosts

# need to change hosts file location on windows
#echo "$public_ip  $vs_hostname" | sudo tee -a /etc/hosts

# set up passwordless ssh
#cat ~/.ssh/id_rsa.pub | ssh root@$public_ip 'cat >> ~/.ssh/authorized_keys'

# copy patch file to server
scp softlayer.patch root@$public_ip:/tmp

# configure salt cloud
ssh root@$public_ip << END_OF_COMMANDS
curl -o /tmp/install_salt.sh -L https://bootstrap.saltstack.com && sh /tmp/install_salt.sh -Z -M git 2015.8
# yum for centos, apt-get for ubuntu
yum install -y python-pip && pip install SoftLayer apache-libcloud
#apt-get install -y python-pip && pip install SoftLayer apache-libcloud
mkdir -p /etc/salt/{cloud.providers.d,cloud.profiles.d}
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
  script_args: -D git v2015.8
  image: CENTOS_7_64
  cpu_number: 1
  ram: 1024
  disk_size:
    - 25
    - 100
  local_disk: True
  hourly_billing: True
  domain: w251final.net
  location: dal05
EOF

# install patch from jonathan's email to allow provisioning multiple disks
#git clone https://gist.github.com/517a92941181f8d2d3d1.git:patch
yum install -y patch
# find doesn't work over ssh?
#find /usr/ -wholename "*salt/cloud/clouds/softlayer.py"
#cd $(dirname $(!! | head -1))
cd /usr/lib/python2.7/site-packages/salt/cloud/clouds
patch -p4 < /tmp/softlayer.patch

END_OF_COMMANDS
