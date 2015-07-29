master=saltspark28
minions=(saltspark28 saltspark29)

echo "sl_centos7_small:" > /etc/salt/cloud.map
for minion in ${minions[@]}; do
    echo "  - ${minion}" >> /etc/salt/cloud.map
done
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
    salt-cp "$minion" /tmp/minion_grains /etc/salt/grains
    salt-cp "$minion" /tmp/mine_functions.conf /etc/salt/minion.d/mine_functions.conf
    # not sure if the following is necessary yet...
    # fqdn="$minion"".w251final.net"
    # salt "$minion" cmd.run "echo -e 'id: $fqdn' > /etc/salt/minion.d/local.conf"
    # salt "$minion" service.restart "salt-minion"
    # salt-key -y -a $fqdn && salt-key -y -d $minion
done

cat > /tmp/master_grains <<EOF
roles:
  - hadoop_master
EOF

salt-cp "$master" /tmp/master_grains /etc/salt/grains

# TODO
# update hosts file
# change ids of minions to fqdn
# restart minions
# accept keys

cat > /etc/salt/master <<EOF
file_roots:
  base:
    - /srv/salt
    - /srv/formulas/hostsfile-formula
    - /srv/formulas/ntp-formula
    - /srv/formulas/sun-java-formula
    - /srv/formulas/hadoop-formula
fileserver_backend:
  - roots
pillar_roots:
  base:
    - /srv/pillar
EOF

cat > /srv/salt/top.sls <<EOF
base:
  '*':
    - hosts
    - root.ssh
    - root.bash_profile
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
      - hostsfile
      - hostsfile.hostname
      - ntp.server
      - sun-java
      - sun-java.env

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

salt-run state.orchestrate orchestration.provision_hadoop
