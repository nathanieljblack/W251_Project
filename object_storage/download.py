import requests
import cPickle

r = requests.get('https://dal05.objectstorage.softlayer.net/v1/AUTH_e79b7d9d-1322-49f1-8ba4-648daeb72572/251_project_data/train_16.cpickle')

#load the pickled file into memory
img_list = cPickle.loads(r.content)

#save to a local file
local_filename = 'd.cpickle'
f = open(local_filename, 'wb')
f.write(r.content)
f.close()

