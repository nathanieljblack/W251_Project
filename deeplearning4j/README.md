#Note this part of the project was abandoned as much of the DL4J library is unstable and being rebuilt

#DeepLearning4J  
DeepLearning4J is a much-hyped Java library for deep learning. The library allows for deep learning frameworks to be built on top of modern big data tools such as Hadoop and Spark while using GPUs on the backend for computation. Currently, other popular deep learning libraries such as Caffe, Torch, and Theano are not built on the Java Virtual Machine (JVM) which makes Hadoop and Spark integration (Hadoop and Spark are built on JVM) difficult. DeepLearning4J has much promise but the project is still very young. During the course of the project, the key functionality for image classification (convolutional and recurrent networks) was not working. The team was able to successfully implement DeepLearning4J on top of Spark but the functionality was extremely limited so the group abandoned the library in favor of more mature libraries such as MLLib and Theano. As DeepLearning4J matures, it will be very interesting to see how complex neural networks can be implemented using both the power of Spark as well as the speed of GPU computation.

##DL4J Setup

On a node with Spark already installed...  

Install from source
```
sudo apt-get update
sudo apt-get install git
sudo apt-get install maven
sudo apt-get default-jdk
sudo apt-get gfortran-4.4
sudo apt-get build-essential
echo "deb https://dl.bintray.com/sbt/debian /" | sudo tee -a /etc/apt/sources.list.d/sbt.list
sudo apt-get update
sudo apt-get install sbt
```

Clone libraries  
```
git clone https://github.com/deeplearning4j/nd4j
git clone https://github.com/deeplearning4j/Canova
git clone https://github.com/deeplearning4j/deeplearning4j
```

Build Source with Maven  
```
cd nd4j
mvn clean install -DskipTests -Dmaven.javadoc.skip=true
cd
cd Canova
mvn clean install -DskipTests -Dmaven.javadoc.skip=true
cd
cd deeplearning4j
mvn clean install -DskipTests -Dmaven.javadoc.skip=true
```


