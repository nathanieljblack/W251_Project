#!/bin/bash

size=$1
train_file=train_$size.csv
test_file=test_$size.csv

/bin/rm -f $train_file
/bin/rm -f $test_file

echo "downloading " $train_file " ..."
wget https://dal05.objectstorage.softlayer.net/v1/AUTH_e79b7d9d-1322-49f1-8ba4-648daeb72572/251_project_data/$train_file

echo "downloading " $test_file " ..."
wget https://dal05.objectstorage.softlayer.net/v1/AUTH_e79b7d9d-1322-49f1-8ba4-648daeb72572/251_project_data/$test_file