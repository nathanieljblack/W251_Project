#Ansible Playbook for Spark and Hadoop

##Download Ansible (on Ubuntu)

```
$ sudo apt-get install software-properties-common
$ sudo apt-add-repository ppa:ansible/ansible
$ sudo apt-get update
$ sudo apt-get install ansible
```

##Set up
###Softlayer

You will need to configure ``/start_cluster/provision.py`` with your Softlayer username, API key, and an SSH key saved on Softlayer.

Get the SSH number with
```
slcli sshkey list
```
###VM Setup
Change ``config.json`` to the desired VM setup.

###RSA Keys
Create an RSA Public/Private pair and save them as ``id_rsa_hadoop`` and ``id_rsa_hadoop.pub`` in the ``/local`` folder

###Hosts

Setup ``hosts`` with 

```
[local]
localhost ansible_connection=local
```

Make sure you have passwordless sudo on your local machine (you can edit ``/etc/sudoers`` to change this). Also make sure you have the correct version of the Python ``Softlayer.API``. Edit the ``start_cluster.yml`` file "shell" line. I think this has to be the full path.

```
shell: <PATH TO PYTHON BIN> <PATH TO provision.py> 3
```

#Start Cluster
Run ``start_cluster.yml`` and specify number of nodes. Default is 3. This will take several minutes and will alter several of the Ansible setup files.

```
ansible-playbook --extra-vars '{"NUM_NODES":"2"}' -s start_cluster.yml -i ./hosts

```

#Set up Cluster

##Vault information

Run the following command in the Ansible directory to encrypt ``main.yml`` and set a password. You can decrypt with the same command replacing decrypt for encrypt.

```
ansible-vault encrypt main.yml
```

##Run Setup script

Run the command below to set up the cluster with Hadoop, Spark, data, etc.

```
ansible-playbook --extra-vars '{"IMAGE_SIZE":"64"}' -s main.yml -i ./hosts --ask-vault-pass
```


#Start Hadoop and Spark

Finally run the ``hadoop.yml`` script to start Spark and Hadoop.

```
ansible-playbook -s hadoop.yml -i ./hosts
```

Partial Run


If you want to run a certain portion of the playbook, specify tags (located under blocks in ``main.yml``)
```
ansible-playbook -s main.yaml -i ./hosts --tags "hadoop"
```

