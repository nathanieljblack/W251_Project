## Convolutional Neural Network

### Preprocess Images
Four VS's were provisioned for preprocessing with 4 cores, 32GB memory, and 100GB harddrive.
Paswordless ssh was set up between all of these VS's.

Preprocessing was performed in parallel on the four VS's.  
Install prereqs:
```
sudo apt-get install build-essential python-dev python-setuptools \
                     python-numpy python-scipy \
                     libatlas-dev libatlas3gf-base
sudo apt-get install python-sklearn
sudo apt-get install python-skimage
sudo apt-get install python-pip
pip install Pillow
```

Distribute images to the four VS's with ``distrImages.py``  
Change list of VS names to match the ones provisioned above and call with the following:
```
python distrImages.py -distribute
```

In preprocessing, first, the images were centered and blank space was cropped to a tight square around the eye, the image was then resized to 1024 by 1020 and saved as jpeg's for more efficient storage and faster processing later. Use the script ``center_trim_resize_1k.py`` on each VS to process images stored there, making sure that the hard-coded directories match those where the original images and processed images are stored. There is also a threshold value for black in the script that should be changed appropriately to process all images with varying quality and lighting (see comment in code).   

After centering and shrinking the images in the first step, synthetic data were created by rotating the images 90-, 180-, and 270-degrees as well as flipping the image and rotating the mirror image as well. These steps create 8x the original data set size. Data augmentation was performed with ``createSyntheticData.py``, with directories for originial images and synthetic data hard-coded in the main().    

The last preprocessing step was to normalize the colors in the images and resize the images to the desired size for training the classifier. ``colornorm_resize_pickle.py`` performed these steps and saved the resulting image arrrays together as a pickle file. The size for resizing is hard-coded into the main function of the script and can be changed there for producing other sizes. We used 128x128 for developing the convolutional neural network classifier.  
The preprocessing steps can be visualized in the ipython notebook ``preprocess_steps.ipynb``.  

### Subsample
Due to the difficulty of this classification problem and after many failed attempts, the problem was simplified for training the model by reducing to a binary classification problem. Only images of the most progressed diabetic retinopathy (labeled 4 in the training set) and a subsample of images with no signs of retinopathy (labeled 0) were used. The script for subsampling from the original images is in ``subsampleImages.py``.  

### Classifier
Convolutional neural networks were trained using Theano, and later, Lasagne and nolearn.

The Theano code is contained in ``theanocnn_04.py``, but there were many versions before this one, with changes to the network architecture, initial weights, and parameter updating.  
This code converged extremely quickly to predicting all one class, even with a very small learning rate, and was abandoned for an solution using Theano extensions, Lasagne and nolearn. Further discussion of the challenges with Theano and benefit of the extentions are discussed in the project report.  

nolearn was ultimately used to build and train a convolutional neural network classifier. nolearn works with Lasagne on top of Theano, and greatly simplifies the process. The convolutional neural network code is in ``nolearncnn_04.py``.

### Running on AWS with GPU
To greatly speed up computations, the models were trained on a GPU on an AWS EC2 instance. AWS was used instead of Softlayer because of the availability of hourly billing and the relatively high cost of a GPU VS.  
A g2.8xlarge EC2 instance with 60GB of memory and 2x120GB of mounted storage was launched with an ssh key. After connecting to the instance the following commands (from http://markus.com/install-theano-on-aws/, http://lasagne.readthedocs.org/en/latest/user/installation.html, and https://pythonhosted.org/nolearn/) are needed to prepare to run the Theano and nolearn code using the GPU:
```
sudo apt-get update
sudo apt-get -y dist-upgrade 
sudo apt-get install -y gcc g++ gfortran build-essential git wget linux-image-generic libopenblas-dev python-dev python-pip python-nose python-numpy python-scipy
sudo pip install --upgrade --no-deps git+git://github.com/Theano/Theano.git  
sudo wget http://developer.download.nvidia.com/compute/cuda/repos/ubuntu1404/x86_64/cuda-repo-ubuntu1404_7.0-28_amd64.deb  
sudo dpkg -i cuda-repo-ubuntu1404_7.0-28_amd64.deb  
sudo apt-get update
sudo apt-get install -y cuda  
echo -e "\nexport PATH=/usr/local/cuda/bin:$PATH\n\nexport LD_LIBRARY_PATH=/usr/local/cuda/lib64" >> .bashrc  
sudo reboot 
echo -e "\n[global]\nfloatX=float32\ndevice=gpu\n[mode]=FAST_RUN\n\n[nvcc]\nfastmath=True\n\n[cuda]\nroot=/usr/local/cuda" >> ~/.theanorc  

sudo pip install -r https://raw.githubusercontent.com/Lasagne/Lasagne/v0.1/requirements.txt
sudp pip install Lasagne==0.1
sudo pip install -r https://raw.githubusercontent.com/dnouri/nolearn/master/requirements.txt
sudo pip install https://github.com/dnouri/nolearn/archive/master.zip#egg=nolearn

sudo pip install Pillow
sudo pip install pandas
```
