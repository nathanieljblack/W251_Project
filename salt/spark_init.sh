#!/bin/bash

# TODO
# [] add command line argument for number of nodes
# git clone repo to get files on saltmaster

master=saltspark79
minions=(saltspark79 saltspark80)

cat > /etc/salt/cloud.profiles.d/softlayer.conf << EOF
small:
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

# create map file used to start multiple instances at once
echo "small:" > /etc/salt/cloud.map
for minion in ${minions[@]}; do
    echo "  - ${minion}" >> /etc/salt/cloud.map
done
salt-cloud -m /etc/salt/cloud.map -P -y

# get private ips and hostnames and store in roster
# !! don't need roster file, should look at minions to determine which
# machines to put in hosts file below
salt '*' network.interface_ip eth0 | sed 'N;s/\n\ \+/ /' > /etc/salt/roster

# configure salt states
mv /etc/salt/master /etc/salt/master~orig
cat > /etc/salt/master << EOF
file_roots:
  base:
    - /srv/salt
fileserver_backend:
  - roots
pillar_roots:
  base:
    - /srv/pillar
EOF

mkdir -p /srv/{salt,pillar} && service salt-master restart

cat > /srv/salt/top.sls <<EOF
base:
  '*':
    - hosts
    - root.ssh
    - root.bash_profile
EOF

# create /srv/salt/hosts.sls
cat > /srv/salt/hosts.sls << EOF
localhost-hosts-entry:
  host.present:
    - ip: 127.0.0.1
    - names:
      - localhost
      - localhost.localdomain
EOF
IFS=$'\n'
lines=""
i=0
# iterate over hostnames and ips already stored in roster file
for line in $(cat /etc/salt/roster) ; do
  ((i++))
  hostname=$(echo $line | awk -F": " '{print $1}')
  privateip=$(echo $line | awk -F": " '{print $2}')
  line1=$(printf "node$i-hosts-entry:")
  line2=$(printf "  host.present:")
  line3=$(printf "    - ip: $privateip")
  line4=$(printf "    - names:")
  line5=$(printf "      - $hostname")
  lines=$(printf "${lines}\n${line1}\n${line2}\n${line3}\n${line4}\n${line5}")
done
printf "%s\n" "$lines" >> /srv/salt/hosts.sls
# set field separator back to default
IFS=$' \t\n'

# set up passwordless ssh
mkdir /srv/salt/sshkeys
ssh-keygen -N '' -f /srv/salt/sshkeys/id_rsa
export PUBLIC_KEY=`cat /srv/salt/sshkeys/id_rsa.pub | cut -d ' ' -f 2`
#sudo salt-cp "$master" /tmp/id_rsa /root/.ssh/id_rsa
#sudo salt-cp "$master" /tmp/id_rsa.pub /root/.ssh/id_rsa.pub

cat > /srv/salt/copyfiles.sls <<EOF
/root/.ssh:
  file.recurse:
    - source: salt://sshkeys
    - user: root
    - group: root
EOF

salt "$master" state.sls copyfiles
salt "$master" cmd.run "chmod 400 /root/.ssh/id_rsa"

cat > /srv/salt/root/ssh.sls <<EOF
$PUBLIC_KEY:
  ssh_auth.present:
    - user: root
    - enc: ssh-rsa
    - comment: root@$master
EOF

cat > /srv/salt/root/bash_profile << EOF
# .bash_profile

# Get the aliases and functions
if [ -f ~/.bashrc ]; then
  . ~/.bashrc
fi

# User specific environment and startup programs
export PATH=$PATH:$HOME/bin
#export JAVA_HOME="$(readlink -f $(which java) | grep -oP '.*(?=/bin)')"
export JAVA_HOME="/usr/lib/jvm/java-1.8.0-openjdk-1.8.0.51-1.b16.el7_1.x86_64/jre"
export SPARK_HOME="/usr/local/spark"
export PATH=$PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin
EOF

cat > /srv/salt/root/bash_profile.sls << EOF
/root/.bash_profile:
  file.managed:
    - source: salt://root/bash_profile
    - overwrite: true
EOF

salt '*' state.highstate
salt '*' cmd.run 'yum install -y java-1.8.0-openjdk-headless'
salt '*' cmd.run "curl http://d3kbcqa49mib13.cloudfront.net/spark-1.4.0-bin-hadoop2.6.tgz | tar -zx -C /usr/local --show-transformed --transform='s,/*[^/]*,spark,'"

cat /dev/null >| /tmp/slaves
for minion in ${minions[@]}; do
    echo "${minion}" >> /tmp/slaves
done

salt-cp "$master" /tmp/slaves /usr/local/spark/conf

salt "$master" cmd.run "/usr/local/spark/sbin/start-master.sh"
salt "$master" cmd.run "/usr/local/spark/sbin/start-slaves.sh"
