cat > /etc/salt/provision_hadoop.sls <<EOF
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
      - hadoop.snappy
      - hadoop.hdfs
      - hadoop.mapred
      - hadoop.yarn
EOF

cat /srv/salt/top.sls

# [] download github formulas
# [] edit /etc/salt/master
#service salt-master restart
# [] add roles hadoop_master and hadoop_slave to /etc/salt/grains
