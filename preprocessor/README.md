##Spark Mapper

A simple preprocessor, `resize_spark_mapper` takes in an image file, and resizes it in the following ways:

- Makes it a square by cutting off extra width or height
- Crops both the height and width by 10% 
- Resizes it to 512 x 512

Using a Spark setup, install the following packages:
- gcc
- gcc-c++
- python-devel
- cython
- numpy
- libjpeg
- libjpeg-devel
- Pillow (upgrade if already installed)

At this time, in order to run this, the following must be satistfied:
- This repository is cloned at the home directory level on all the nodes
- All the above packages need to be installed on all the nodes

Then, run the following:

```
cp /root/W251_Project/preprocessor/resize_spark_mapper.py ~
cd ~
$SPARK_HOME/bin/spark-submit resize_spark_mapper.py <test_or_train> <image_size> <directory_with_image_files>
```
        
The preprocessed files will be saved at `/root/W251_Project/preprocessor/<test_or_train>_<image_size>`.    
This also generates a `<test_or_tran>_<image_size>.csv` file which contains the flattened arrays corresponding to all images stored as Comma Separated Values (csv).
