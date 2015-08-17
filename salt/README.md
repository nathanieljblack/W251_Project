### Using SaltStack to Configure a Cluster

#### Step 1: Create a *Salt Master*
From your local machine, run the script saltcloud_init.sh to provision a Salt Master VS.

```Shell
./saltcloud_init.sh -u SLxxxxxx -k … -h saltmaster -i mids
```

The required arguments are:
 - -u: SoftLayer username (alternatively set ST_USER environment variable)
 - -k: Softlayer API key (alternatively set ST_KEY environment variable)
 - -h: Hostname for virtual server
 - -i: SSH key identifier

During the provisioning, it is necessary to type *yes* (to add the VS to known_hosts) and enter the root password (printed to stdout after the VS is provisioned) **twice**. The script will error out if the provisioned virtual server has an IP that was previously added to the local known_hosts file.

#### Step 2: Provision a Cluster
SSH to the *Salt Master*, and run the script hdfs_spark_init.v2.sh.

```Shell
git clone https://github.com/nathanieljblack/W251_Project.git
cd W251_Project/salt
chmod +x hdfs_spark_init.v2.sh
./hdfs_spark_init.v2.sh
```

If this script fails, it can be rerun indefinitely until it is successful. Creating the hosts file will fail periodically if one of the minions times out before it returns its private ip. This script must be run initially with new hostnames so that Salt Cloud will accept the minion's key.

#### Step 3: SSH to Master
SSH to the master (see the 1st line of hdfs_spark_init.v2.sh) and run Spark jobs!

You can test that HDFS is working by running the following commands.

```Shell
touch test
hadoop fs -put test /
hadoop fs -ls /
```
