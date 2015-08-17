# W251_Project
## Katie Adams, Kevin Allen, Nate Black, and Malini Mittal  

This project explores different methods of large-scale image classification. The first method uses the Apache Spark framework while the second uses deep learning on GPUs with Python's Theano library.

##General Dataset Information
Created a test VM to test the download time of the training data. Ran into some issues using ``wget`` to download the data - you need to be a registered user to download the data. Therefore, you must copy your local cookies into a text file and pass that to the ``wget`` call (or do some other workaround). Commands below.

```
[root@test ~]# mkdir data
[root@test ~]# cd data
[root@test data]# nano cookies.txt
[root@test data]# wget -x --load-cookies cookies.txt https://www.kaggle.com/c/diabetic-retinopathy-detection/download/train.zip.00{1..5}
```  

Download took an hour with ``network=1000`` on the VM.
```
FINISHED --2015-06-15 19:04:53--
Downloaded: 5 files, 33G in 1h 1m 28s (9.05 MB/s)
```
#How Big is Unzipped Training Data?  
The training files are pieces of a single archive so they were combined and then unzipped. Deleted the individual zip components to save space. Unzip took ~30 minutes.

```
[root@test download]# cat train.zip.00* > train.zip
[root@test download]# unzip train.zip
```

35,126 images - 33 GB zipped, 36GB unzipped
```
[root@test download]# ls
train  train.zip
[root@test download]# ls -1 train | wc -l
35126
[root@test download]# du -sh *
36G	train
33G	train.zip

```

Case Information
```
Cases     Level			Proportion

25810  0 - No DR             73%
 2443  1 - Mild               7%
 5292  2 - Moderate          15%
  873  3 - Severe             2%
  708  4 - Proliferative DR   2%
35126  Total
```
##Single Machine Attempt
`single_machine_attempt` was an exploratory analysis and provided evidence that the problem was too large for a single machine. The `single_machine_attempt/README.md` outlines some of the key findings and shows sample output from the analysis.  

##Scala Logistic Regression  
`scala_logistic_regression` outlines the development of the logistic regression classifier used for Spark. The classifier was developed using the local file system and then augmented to run on HDFS after the code was functional. Note the code in this directory is not the final code used for either the pre-processor or the classifier but was left in the repo for informational purposes.  

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

