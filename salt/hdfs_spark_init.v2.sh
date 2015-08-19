master=master11
minions=($master minion25 minion26)
domain=w251final.net

cat > /etc/salt/cloud.profiles.d/softlayer.conf <<EOF
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
  domain: $domain
  location: dal05
EOF

echo "small:" > /etc/salt/cloud.map
for minion in ${minions[@]}; do
    echo "  - ${minion}" >> /etc/salt/cloud.map
done
salt-cloud -m /etc/salt/cloud.map -P -y

rm -rf /srv/{salt,pillar} && mkdir -p /srv/{salt,pillar}

#salt -C '*minion* or *master*' service.restart "salt-minion"
service salt-master restart
sleep 15

cat > /srv/salt/install_hadoop.sh <<EOF
yum install -y java-1.6.0-openjdk*
yum install -y java-1.8.0-openjdk-headless
curl http://d3kbcqa49mib13.cloudfront.net/spark-1.4.0-bin-hadoop2.6.tgz | tar -zx -C /usr/local --show-transformed --transform='s,/*[^/]*,spark,'
wget http://apache.claz.org/hadoop/core/hadoop-2.6.0/hadoop-2.6.0.tar.gz
tar xzf hadoop-2.6.0.tar.gz
mv hadoop-2.6.0 hadoop
EOF

cat > /srv/salt/mountfs.sh <<EOF
mount /data
exit 0
EOF

cat > /srv/salt/hadoop_user.sls <<EOF
hadoop:
  group.present:
    - gid: 6000
  user.present:
    - uid: 6000
    - gid: 6000
    - home: /home/hadoop
    - groups:
      - hadoop
    - require:
      - group: hadoop
EOF

cat > /srv/salt/provision_hdfs.sls <<EOF
include:
  - hadoop_user

/tmp/install_hadoop.sh:
  file.managed:
    - source: salt://install_hadoop.sh
    - user: root
    - group: root
    - mode: 500

install_hadoop:
  cmd.run:
    - name: /tmp/install_hadoop.sh
    - cwd: /usr/local
    - unless:
      - ls /usr/local/hadoop

/tmp/mountfs.sh:
  file.managed:
    - source: salt://mountfs.sh
    - user: root
    - group: root
    - mode: 500

makefs:
  cmd.run:
    - name: mkfs.ext4 /dev/xvdc
    - unless:
      - ls /data
    - require_in:
      - file: /data

mountfs:
  cmd.run:
    - name: /tmp/mountfs.sh
    - require:
      - cmd: makefs
      - file: /etc/fstab
      - file: /tmp/mountfs.sh

/data:
  file.directory:
    - user: hadoop
    - group: hadoop
    - require:
      - sls: hadoop_user

/usr/local/hadoop:
  file.directory:
    - user: hadoop
    - group: hadoop
    - require:
      - sls: hadoop_user

  # mount.mounted:
  #   - device: /dev/xvdc
  #   - fstype: ext4
  #   - mkmnt: True

/etc/fstab:
  file.append:
    - text:
      - "/dev/xvdc /data                   ext4    defaults,noatime        0 0"
EOF

# set up hosts file
i=0
cat /dev/null > /srv/salt/hosts.sls
for minion in ${minions[@]}; do
    ((i++))
    privateip=$(salt -t 60 "$minion" network.interface_ip eth0 | sed -n 2p)
    cat >> /srv/salt/hosts.sls <<EOF
node$i-hosts-entry:
  host.present:
    - ip: $privateip
    - names:
      - $minion
EOF
done

# set up passwordless ssh for root and hadoop users
# only create the keys if the directory doesn't exist
mkdir /srv/salt/{root,hadoop}
mkdir /srv/salt/{root,hadoop}/sshkeys && ssh-keygen -N '' -f /srv/salt/root/sshkeys/id_rsa && ssh-keygen -N '' -f /srv/salt/hadoop/sshkeys/id_rsa
export ROOT_PK=`cat /srv/salt/root/sshkeys/id_rsa.pub | cut -d ' ' -f 2`
export HADOOP_PK=`cat /srv/salt/hadoop/sshkeys/id_rsa.pub | cut -d ' ' -f 2`

cat > /srv/salt/ssh.sls <<EOF
$ROOT_PK:
  ssh_auth.present:
    - user: root
    - enc: ssh-rsa
    - comment: root@$master
    - require_in:
      - file: /root/.ssh

/root/.ssh:
  file.recurse:
    - source: salt://root/sshkeys
    - user: root
    - group: root

/root/.ssh/id_rsa:
  file.managed:
    - mode: 400
    - user: root
    - group: root
    - require:
      - file: /root/.ssh

$HADOOP_PK:
  ssh_auth.present:
    - user: hadoop
    - enc: ssh-rsa
    - comment: hadoop@$master
    - require_in:
      - file: /home/hadoop/.ssh

/home/hadoop/.ssh:
  file.recurse:
    - source: salt://hadoop/sshkeys
    - user: hadoop
    - group: hadoop

/home/hadoop/.ssh/id_rsa:
  file.managed:
    - mode: 400
    - user: hadoop
    - group: hadoop
    - require:
      - file: /home/hadoop/.ssh
EOF

cat > /srv/salt/bash_profile <<EOF
# .bash_profile

# Get the aliases and functions
if [ -f ~/.bashrc ]; then
  . ~/.bashrc
fi

# User specific environment and startup programs
#export JAVA_HOME="$(readlink -f $(which java) | grep -oP '.*(?=/bin)')"
export JAVA_HOME=/usr/lib/jvm/java-1.8.0-openjdk-1.8.0.51-1.b16.el7_1.x86_64/jre
export SPARK_HOME=/usr/local/spark
export PATH=$PATH:$HOME/bin:/usr/local/hadoop/bin:/usr/local/spark/bin:/usr/local/spark/sbin
EOF

cat > /srv/salt/bash_profile.sls <<EOF
/root/.bash_profile:
  file.managed:
    - source: salt://bash_profile
    - overwrite: true

/home/hadoop/.bash_profile:
  file.managed:
    - source: salt://bash_profile
    - overwrite: true
EOF

cat /dev/null > /srv/salt/slaves
for minion in ${minions[@]}; do
  echo "$minion" >> /srv/salt/slaves
done

cat > /srv/salt/hadoop_master_conf.sls <<EOF
/usr/local/hadoop/etc/hadoop/masters:
  file.append:
    - text:
      - "$master"

/usr/local/hadoop/etc/hadoop/slaves:
  file.managed:
    - source: salt://slaves
    - overwrite: true

/usr/local/spark/conf/slaves:
  file.managed:
    - source: salt://slaves
    - overwrite: true
EOF

cat > /srv/salt/core-site.xml <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<configuration>
<property>
<name>fs.default.name</name>
<value>hdfs://$master:9000</value>
</property>
</configuration>
EOF

cat > /srv/salt/hdfs-site.xml <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<configuration>
<property>
<name>dfs.replication</name>
<value>${#minions[@]}</value>
</property>
<property>
<name>dfs.data.dir</name>
<value>/data</value>
</property>
</configuration>
EOF

cat > /srv/salt/hadoop_conf.sls <<EOF
include:
  - provision_hdfs

/usr/local/hadoop/etc/hadoop/core-site.xml:
  file.managed:
    - source: salt://core-site.xml
    - overwrite: true
    - require:
      - sls: provision_hdfs

/usr/local/hadoop/etc/hadoop/hdfs-site.xml:
  file.managed:
    - source: salt://hdfs-site.xml
    - overwrite: true
    - require:
      - sls: provision_hdfs

/usr/local/hadoop/etc/hadoop/hadoop-env.sh:
  file.append:
    - text:
      - "export JAVA_HOME=/usr/lib/jvm/java-1.8.0-openjdk-1.8.0.51-1.b16.el7_1.x86_64/jre"
EOF

cat > /srv/salt/start_master.sh <<EOF
source ~/.bash_profile
/usr/local/hadoop/sbin/stop-all.sh
jps | grep "NameNode" | cut -d " " -f 1 | xargs kill
sleep 10
yes | hadoop namenode -format
/usr/local/hadoop/sbin/hadoop-daemon.sh --config /usr/local/hadoop/etc/hadoop --script hdfs start namenode

/usr/local/spark/sbin/stop-all.sh
/usr/local/spark/sbin/start-master.sh
/usr/local/spark/sbin/start-slaves.sh
EOF

cat > /srv/salt/start_master.sls <<EOF
/tmp/start_master.sh:
  file.managed:
    - source: salt://start_master.sh
    - user: root
    - group: root
    - mode: 500

start_master:
  cmd.run:
    - name: /tmp/start_master.sh
    - require:
      - file: /tmp/start_master.sh
EOF

cat > /srv/salt/start_slaves.sh <<EOF
source ~/.bash_profile
jps | grep "DataNode" | cut -d " " -f 1 | xargs kill
sleep 10
/usr/local/hadoop/sbin/hadoop-daemon.sh --config /usr/local/hadoop/etc/hadoop --script hdfs start datanode
EOF

cat > /srv/salt/start_slaves.sls <<EOF
/tmp/start_slaves.sh:
  file.managed:
    - source: salt://start_slaves.sh
    - user: root
    - group: root
    - mode: 500

start_slaves:
  cmd.run:
    - name: /tmp/start_slaves.sh
    - require:
      - file: /tmp/start_slaves.sh
EOF

cat > /etc/salt/master <<EOF
file_roots:
  base:
    - /srv/salt
fileserver_backend:
  - roots
pillar_roots:
  base:
    - /srv/pillar
EOF

cat > /srv/salt/top.sls <<EOF
base:
  '*':
    - provision_hdfs
    - hosts
    - ssh
    - bash_profile
    - hadoop_conf
    - hadoop_user
  '*master*':
    - hadoop_master_conf
EOF

salt -t 120 '*' state.highstate
salt -t 120 '*master*' state.sls start_master
salt -t 120 '*minion*' state.sls start_slaves
