#How Long to Download Training Data?
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

