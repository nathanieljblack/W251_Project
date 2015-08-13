master=saltspark99
minions=(saltspark100 saltspark101)
domain=w251final.net

echo "small:" > /etc/salt/cloud.map
for minion in ${minions[@]}; do
    echo "  - ${minion}" >> /etc/salt/cloud.map
done
echo "  - $master" >> /etc/salt/cloud.map
salt-cloud -m /etc/salt/cloud.map -P -y

mkdir -p /srv/formulas
cd /srv/formulas
git clone https://github.com/saltstack-formulas/hostsfile-formula.git
git clone https://github.com/saltstack-formulas/ntp-formula.git
git clone https://github.com/saltstack-formulas/sun-java-formula.git
git clone https://github.com/saltstack-formulas/hadoop-formula.git

service salt-master restart

cat > /srv/salt/hdfs.sh <<EOF
mkdir -m 777 /data
mkfs.ext4 /dev/xvdc
EOF

cat > /srv/salt/provision_hdfs.sls <<EOF
  cmd.test:
    cmd.script:
      - source: salt://hdfs.sh
      - cwd: /
      - user: root

  /etc/fstab:
    file.append:
      - text:
        - "/dev/xvdc /data                   ext4    defaults,noatime        0 0"

  /etc/salt/minion.d/mine_functions.conf:
    file.append:
    - text:
      - "mine_functions:"
      - "  network.interfaces: []"
      - "  network.ip_addrs:"
      - "    - eth0"
      - "  grains.items: []"
EOF

salt '*' state.apply provision_hdfs
salt '*' cmd.run 'mount /data'

# set grains on master and minions to target hadoop services
cat > /tmp/minion_grains <<EOF
roles:
  - hadoop_slave
hdfs_data_disks:
  - /data
EOF

for minion in ${minions[@]}; do
    salt-cp "$minion" /tmp/mine_functions.conf /etc/salt/minion.d/mine_functions.conf
    # change minion id to fqdn
    fqdn="$minion"".w251final.net"
    salt "$minion" cmd.run "echo -e 'id: $fqdn' > /etc/salt/minion.d/local.conf"
    salt "$minion" service.restart "salt-minion"
    sleep 15
    salt-key -y -a $fqdn && salt-key -y -d $minion
    salt-cp "$minion.$domain" /tmp/minion_grains /etc/salt/grains
done

salt-cp "$master" /tmp/mine_functions.conf /etc/salt/minion.d/mine_functions.conf
# change minion id to fqdn
fqdn="$master.$domain"
salt "$master" cmd.run "echo -e 'id: $fqdn' > /etc/salt/minion.d/local.conf"
salt "$master" service.restart "salt-minion"
sleep 15
salt-key -y -a $fqdn && salt-key -y -d $master
salt-cp "$master.$domain" /tmp/minion_grains /etc/salt/grains

# not able to run datanode on master, targeting multiple grains seems broken
cat > /tmp/master_grains <<EOF
roles:
  - hadoop_slave
  - hadoop_master
EOF

salt-cp "$master.$domain" /tmp/master_grains /etc/salt/grains

#
cat > /etc/salt/master <<EOF
file_roots:
  base:
    - /srv/salt
    - /srv/formulas/ntp-formula
    - /srv/formulas/sun-java-formula
    - /srv/formulas/hadoop-formula
    - /srv/formulas/hostsfile-formula
fileserver_backend:
  - roots
pillar_roots:
  base:
    - /srv/pillar
EOF

# - hosts
# - root.ssh
# - root.bash_profile
cat > /srv/salt/top.sls <<EOF
base:
  '*':
    - provision_hdfs
    - provision_hadoop
    - hadoop
    - hadoop.hdfs
EOF

mkdir /srv/salt/orchestration

cat > /srv/salt/orchestration/provision_hadoop.sls <<EOF
prep:
  salt.state:
    - tgt: '*'
    - sls:
      - ntp.server
      - sun-java
      - sun-java.env
      - hostsfile
      - hostsfile.hostname

hadoop_services:
  salt.state:
    - tgt: 'G@roles:hadoop_master or G@roles:hadoop_slave'
    - tgt_type: compound
    - require:
      - salt: prep
    - sls:
      - hadoop
      - hadoop.hdfs
EOF

cat > /srv/pillar/top.sls <<EOF
base:
  'G@roles:hadoop_slave or G@roles:hadoop_master':
    - hadoop
EOF

cat > /srv/pillar/hadoop.sls <<EOF
hadoop:
  version: hdp-1.6.0
  users:
    hadoop: 6000
    hdfs: 6001
EOF

# for some reason, need to manually generate keys
/srv/formulas/hadoop-formula/hadoop/files/generate_keypairs.sh

service salt-master restart

salt-run state.orchestrate orchestration.provision_hadoop
