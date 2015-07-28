master=saltspark26
minions=(saltspark26 saltspark27)

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

cat > /tmp/salt/minion

for minion in ${minions[@]}; do
    salt-cp "$minion" /tmp/minion_grains /etc/salt/grains
    salt-cp "$minion" /tmp/mine_functions.conf /etc/salt/minion.d/mine_functions.conf
done

cat > /tmp/master_grains <<EOF
roles:
  - hadoop_master
  - hadoop_slave
hdfs_data_disks:
  - /data
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

salt-run state.orchestrate orchestration.provision_hadoop

# cat > /srv/pillar/top.sls <<EOF
# hadoop:
#   version: apache-1.2.1 # ['apache-1.2.1', 'apache-2.2.0', 'hdp-1.3.0', 'hdp-2.2.0', 'cdh-4.5.0', 'cdh-4.5.0-mr1']
#   targeting_method: grain # [compound, glob] also supported
#   users:
#     hadoop: 6000
#     hdfs: 6001
#   config:
#     directory: /etc/hadoop/conf
#     core-site:
#       io.native.lib.available:
#         value: true
#       io.file.buffer.size:
#         value: 65536
#       fs.trash.interval:
#         value: 60
#
# hdfs:
#   namenode_target: "roles:hadoop_master" # Specify compound matching string to match all your namenodes
#   datanode_target: "roles:hadoop_slave" # Specify compound matching string to match all your datanodes e.g. if you were to use pillar I@datanode:true
#   config:
#     namenode_port: 8020
#     namenode_http_port: 50070
#     secondarynamenode_http_port: 50090
#     # the number of hdfs replicas is normally auto-configured for you in hdfs.settings
#     # according to the number of available datanodes
#     # replication: 1
#     hdfs-site:
#       dfs.permission:
#         value: false
#       dfs.durable.sync:
#         value: true
#       dfs.datanode.synconclose:
#         value: true
# EOF

# [] download github formulas
# [] edit /etc/salt/master
#service salt-master restart
# [] add roles hadoop_master and hadoop_slave to /etc/salt/grains
