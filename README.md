# W251_Project
## Katie Adams, Kevin Allen, Nate Black, and Malini Mittal  

This project explores different methods of large-scale image classification. The first method uses the Apache Spark framework while the second uses deep learning on GPUs with Python's Theano library.

##Spark
The Spark aspect of the project can be accessed by first going through the instructions in the `ansible` or `salt` directories to launch a cluster. After going through the `ansible/README.md` the user will have a running SoftLayer cluster with both Hadoop and Spark running. `sp1` will be the master node.

Relevant URLS  
- `https://<MASTER IP>:8080` Spark Cluster
- `https://<MASTER IP>:4040` Spark Job
- `https://<MASTER IP>:50070` HDFS


The logistic regression classification can be run as `hadoop` user in `/home/hadoop`.  

The user must build the project with SBT.

```
su - hadoop
cd
sbt assembly
```

After the project is built, use `spark-submit` to run the process.

```
ADD SPARK SUBMIT COMMAND HERE
```

After the process runs, an output file will be in the `/home/hadoop/` directory. This file is in the needed format for a Kaggle submission.

