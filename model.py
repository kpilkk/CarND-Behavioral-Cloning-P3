from urllib.request import urlretrieve
import os
import numpy as np
from sklearn.preprocessing import LabelBinarizer
from zipfile import ZipFile

def download(url, file):
    if not os.path.isfile(file):
        print("Download file... " + file + " ...")
        urlretrieve(url,file)
        print("File downloaded")

download('https://s3.amazonaws.com/video.udacity-data.com/topher/2016/December/584f6edd_data/data.zip','data.zip') #s3 path of the dataset provided by udacity

print("All the files are downloaded")

def uncompress_features_labels(dir,name):
    if(os.path.isdir(name)):
        print('Data extracted')
    else:
        with ZipFile(dir) as zipf:
            zipf.extractall('data')
uncompress_features_labels('data.zip','data')

def data_Files(mypath):
    onlyfiles = [f for f in os.listdir(mypath) if os.path.isfile(os.path.join(mypath, f))]
    print(onlyfiles)

print('All files downloaded and extracted')

#Importing Required libraries to make the model work
import os
import csv


samples = [] #simple array to append all the entries present in the .csv file

with open('./data/data/driving_log.csv') as csvfile: #currently after extracting the file is present in this path
    reader = csv.reader(csvfile)
    next(reader, None) #this is necessary to skip the first record as it contains the headings
    for line in reader:
        samples.append(line)

# End- Extra Code to append samples from manually created data

print("Done")


from sklearn.utils import shuffle
from sklearn.model_selection import train_test_split

train_samples, validation_samples = train_test_split(samples,test_size=0.2) #simply splitting the dataset to train and validation set usking sklearn. .15 indicates 20% of the dataset is validation set

import cv2
import numpy as np
import sklearn
import matplotlib.pyplot as plt

#code for generator
def generator(samples, batch_size=32):
    num_samples = len(samples)
   
    while 1: 
        shuffle(samples) #shuffling the total images
        for offset in range(0, num_samples, batch_size):
            
            batch_samples = samples[offset:offset+batch_size]

            images = []
            angles = []
            for batch_sample in batch_samples:
                    for i in range(0,3): #we are taking 3 images, first one is center, second is left and third is right
                        
                        name = './data/data/IMG/'+batch_sample[i].split('/')[-1]
                        center_image = cv2.cvtColor(cv2.imread(name), cv2.COLOR_BGR2RGB) #since CV2 reads an image in BGR we need to convert it to RGB since in drive.py it is RGB
                        center_angle = float(batch_sample[3]) #getting the steering angle measurement
                        images.append(center_image)
                        
                        # introducing correction for left and right images
                        # if image is in left we increase the steering angle by 0.2
                        # if image is in right we decrease the steering angle by 0.2
                        
                        if(i==0):
                            angles.append(center_angle)
                        elif(i==1):
                            angles.append(center_angle+0.2)
                        elif(i==2):
                            angles.append(center_angle-0.2)
                        
                        # Code for Augmentation of data.
                        # We take the image and just flip it and negate the measurement
                        
                        images.append(cv2.flip(center_image,1))
                        if(i==0):
                            angles.append(center_angle*-1)
                        elif(i==1):
                            angles.append((center_angle+0.2)*-1)
                        elif(i==2):
                            angles.append((center_angle-0.2)*-1)
                        #here we got 6 images from one image    
                        
        
            X_train = np.array(images)
            y_train = np.array(angles)
            
            yield sklearn.utils.shuffle(X_train, y_train) #here we do not hold the values of X_train and y_train instead we yield the values which means we hold until the generator is running
            

# compile and train the model using the generator function
train_generator = generator(train_samples, batch_size=32)
validation_generator = generator(validation_samples, batch_size=32)



from keras.models import Sequential
from keras.layers.core import Dense, Flatten, Activation, Dropout
from keras.layers import Conv2D
from keras.layers import Lambda, Cropping2D

model = Sequential()

# Preprocess incoming data, centered around zero with small standard deviation 
model.add(Lambda(lambda x: (x / 255.0) - 0.5, input_shape=(160,320,3)))

# trim image to only see section with road
# i.e. from top, bottom and no cropping from left and right
model.add(Cropping2D(cropping=((70,25),(0,0))))           

#layer 1- Convolution, no of filters- 24, filter size= 5x5, stride= 2x2
model.add(Conv2D(24,(5,5), strides=(2,2), activation='relu'))
# model.add(Activation('relu'))

#layer 2- Convolution, no of filters- 36, filter size= 5x5, stride= 2x2
model.add(Conv2D(36,(5,5), strides=(2,2), activation='relu'))
# model.add(Activation('relu'))

#layer 3- Convolution, no of filters- 48, filter size= 5x5, stride= 2x2
model.add(Conv2D(48,(5,5), strides=(2,2), activation='relu'))
# model.add(Activation('relu'))

#layer 4- Convolution, no of filters- 64, filter size= 3x3, stride= 1x1
model.add(Conv(64,(3,3), activation = 'relu'))
# model.add(Activation('relu'))

#layer 5- Convolution, no of filters- 64, filter size= 3x3, stride= 1x1
model.add(Conv(64,(3,3)))
# model.add(Activation('relu'))

#flatten image from 2D to side by side
model.add(Flatten())

#layer 6- fully connected layer 1
model.add(Dense(100, activation='relu',))
# model.add(Activation('relu'))

#Adding a dropout layer to avoid overfitting. Here we are have given the dropout rate as 25% after first fully connected layer
model.add(Dropout(0.25))

#layer 7- fully connected layer 1
model.add(Dense(50, activation='relu',))
# model.add(Activation('relu'))


#layer 8- fully connected layer 1
model.add(Dense(10, activation='relu',))
# model.add(Activation('relu'))

#layer 9- fully connected layer 1
model.add(Dense(1)) #here the final layer will contain one value as this is a regression problem and not classification


# the output is the steering angle
# using mean squared error loss function as it is a regression problem
# adam optimizer is used here
model.compile(loss='mse',optimizer='adam')


#fit generator is used here as the number of images are generated by the generator
# no of epochs : 5

model.fit_generator(train_generator, samples_per_epoch= len(train_samples), validation_data=validation_generator,   nb_val_samples=len(validation_samples), nb_epoch=5, verbose=1)

#saving model
model.save('model.h5')

print('Done! Model Saved!')

# keras method to print the model summary
model.summary()