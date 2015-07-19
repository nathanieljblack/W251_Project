Overview of running logistic regression on Spark (no HDFS)

#Requirements  

1GB NICS, 8-16GB RAM per node, enough storage to be able to download and work with the JPEGS, as many cores as possible.

```
sudo yum install gcc-gfortran gcc44-gfortran libgfortran lapack blas python-devel
```
-install JDK
-install numpy
-mount disk  
-install sbt  
-install spark 1.4.0  
-download data  

#Pipe JPEGs through Python Script  

``imageArrayPipe.py`` formats each JPEG into a Numpy array, appends image label, and then outputs a comma-separated stream. Depending on the size of the arrays, it takes 30-120 minutes.

```
for f in *.jpeg; do python imageArrayPipe.py $f >> arrayFile.txt; done;
```

Sample output looks like this...

```
10005_right,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,3,2,8,17,22,28,11,21,23,15,27,27,14,26,26,11,17,17,9,18,15,15,27,25,17,27,26,8,16,18,8,21,14,14,18,17,15,17,16,13,18,21,12,20,22,8,19,15,0,1,2,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
```

Note that the training and test pipes are slightly different due to the data labels.


#Build File

``build.sbt`` file looks like this:

```
name := "LogisticRegression"

version := "1.0"

mergeStrategy in assembly <<= (mergeStrategy in assembly) { (old) =>
   {
    case PathList("META-INF", xs @ _*) => MergeStrategy.discard
    case x => MergeStrategy.first
   }
}

libraryDependencies += "org.apache.spark" % "spark-core_2.10" % "1.0.2"

libraryDependencies += "org.apache.spark" % "spark-mllib_2.10" % "1.4.0"

libraryDependencies += "com.github.fommil.netlib" % "all" % "1.1.2"

resolvers += "Akka Repository" at "http://repo.akka.io/releases/"
```

#Assembly File

``assembly.sbt`` file looks like this:

```
resolvers += Resolver.url("sbt-plugin-releases-scalasbt", url("http://repo.scala-sbt.org/scalasbt/sbt-plugin-releases/"))

addSbtPlugin("com.eed3si9n" % "sbt-assembly" % "0.12.0")
```

#Logistic Regression 

``logisticRegression.scala`` runs the logistic regression. It pulls in a training text file and a test text file.


#Spark Submit

Depending on the cluster, adjust ``--executor-memory``, ``--num-executors``, and ``--executor-cores``.

```
$SPARK_HOME/bin/spark-submit --class "w251.project.logisticregression.LogisticRegression" --master spark://s1:7077 --executor-memory 6g /root/target/scala-2.10/LogisticRegression-assembly-1.0.jar
```

#Sample Output

Still need to re-format the output file before submitting to Kaggle (add header, correct format).

```
Precision = 0.737452283330977                                                   
F1 = 0.737452283330977
Recall = 0.737452283330977

===Confusion Matrix ===
5207.0  1.0  19.0  2.0  6.0  
492.0   0.0  4.0   0.0  0.0  
1025.0  0.0  9.0   1.0  1.0  
169.0   0.0  1.0   0.0  0.0  
132.0   0.0  4.0   0.0  0.0 
```