##Simple Mapper

A simple preprocessor, `resize_mapper` takes in an image file, and resizes it in the following ways:

- Makes it a square by cutting off extra width or height
- Crops both the height and width by 10% 
- Resizes it to 512 x 512

I used the spark setup provisioned for hw6. I had to install the following packages:
- gcc
- gcc-c++
- python-devel
- cython
- numpy
- libjpeg
- libjpeg-devel
- Pillow (upgrade if already installed)

To run, create a file with a list of image files to be preprocessed (`jpeg_files_sample.txt` contains the list of the sample image files). The output image file is saved in a directory called `preprocessed`.

`./resize_mapper.py < jpeg_files_sample.txt`

##Spark Mapper   

This is a spark version of the same preprocessor as above. At this time, in order to run this, the following must be satistfied:
- The repository is cloned at the home directory level on all the nodes
- All the above packages need to be installed on all the nodes

Then, run the following:

```
cp /root/W251_Project/preprocessor/resize_spark_mapper.py ~
cp /root/W251_Project/preprocessor/jpeg_files_sample.txt ~
cd ~
$SPARK_HOME/bin/spark-submit resize_spark_mapper.py jpeg_files_sample.txt
```
        
The preprocessed files will be saved at `/root/W251_Project/preprocessor/preprocessed`.
