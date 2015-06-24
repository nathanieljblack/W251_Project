A simple preprocessor, *resize_mapper* takes in an image file, and resizes it in the following ways:

- Makes it a square by cutting off extra width or height
- Crops both the height and width by 10% 
- Resizes it to 512 x 512

I used the spark setup provisioned for hw6. I had to install the following packages:
- gcc
- gcc-c++
- python-devel
- cython
- scipy
- numpy
- freetype
- freetype-devel
- libpng
- libpng-devel
- libjpeg
- libjpeg-devel
- Pillow (upgrade if already installed)
- six (reinstall a newer version)
- scikit-image

To run, create a file with a list of image files to be preprocessed ( *jpeg_files_sample.txt* contains the list of the sample image files). The output image file is saved in a directory called *preprocessed*.

`./resize_mapper.py < jpeg_files_sample.txt`
