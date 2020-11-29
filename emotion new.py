import sys
import os
import numpy as np
from keras.models import Sequential
from keras.layers import Dense,Dropout,Activation,Flatten
from keras.layers import Conv2D,MaxPooling2D,BatchNormalization
from keras.losses import categorical_crossentropy
from keras.optimizers import Adam
from keras.regularizers import l2
from keras.utils import np_utils

X_train,train_y,X_test,test_y = [],[],[],[]

import pymysql
con = pymysql.connect('localhost','root','15975346Ri','facerecognition')
cur = con.cursor()

cur.execute("SELECT * FROM facefile where Usages='Training'")
rows = cur.fetchall()
for row in rows:
	val = row[1].split(" ")
	X_train.append(np.array(val,'float32'))
	train_y.append(row[0])

cur.execute("SELECT * FROM facefile where Usages='PublicTest'")
rows = cur.fetchall()
for row in rows:
	val = row[1].split(" ")
	X_test.append(np.array(val,'float32'))
	test_y.append(row[0])

#print(X_train[0:2])
#print(train_y[0:2])
#print(X_test[0:2])
#print(test_y[0:2])

#in order to normalize
X_train = np.array(X_train,'float32')
train_y = np.array(train_y,'float32')
X_test = np.array(X_test,'float32')
test_y = np.array(test_y,'float32')

# normalizing data between 0 and 1
X_train -= np.mean(X_train , axis = 0)
X_train /= np.std(X_train , axis = 0)
X_test -= np.mean(X_test , axis = 0)
X_test /= np.std(X_test , axis = 0)

# reshaping data
num_features = 64
num_labels = 7
batch_size = 64
epochs = 1000
width,height = 48,48

X_train = X_train.reshape(X_train.shape[0],width,height,1)
X_test = X_test.reshape(X_test.shape[0],width,height,1)

train_y = np_utils.to_categorical(train_y,num_classes=num_labels)
test_y = np_utils.to_categorical(test_y,num_classes=num_labels)

print("length of xtrain = ",len(X_train))
print("length of ytrain = ",len(train_y))

# designing in cnn
model = Sequential()

# 1st layer
model.add(Conv2D(num_features,kernel_size=(3,3),activation='relu',input_shape=(X_train.shape[1:])))
model.add(Conv2D(num_features,kernel_size=(3,3),activation='relu'))
model.add(MaxPooling2D(pool_size=(2,2),strides=(2,2)))
model.add(Dropout(0.5)) #removing overfitting

# 2nd layer
model.add(Conv2D(num_features,(3,3),activation='relu'))
model.add(Conv2D(num_features,(3,3),activation='relu'))
model.add(MaxPooling2D(pool_size=(2,2),strides=(2,2)))
model.add(Dropout(0.5)) #removing overfitting

# 3rd layer
model.add(Conv2D(2*(num_features),(3,3),activation='relu'))
model.add(Conv2D(2*num_features,(3,3),activation='relu'))
model.add(MaxPooling2D(pool_size=(2,2),strides=(2,2)))

# flattening function
model.add(Flatten())

# adding dense layers
model.add(Dense(2*2*2*2*num_features,activation='relu'))
model.add(Dropout(0.2))
model.add(Dense(2*2*2*2*num_features,activation='relu'))
model.add(Dropout(0.2))

# final layer
model.add(Dense(num_labels,activation='softmax')) #activation=softmax because we are classifying our model in tems of labels

model.compile(loss=categorical_crossentropy,optimizer=Adam(),metrics=['accuracy'])

model.fit(X_train,train_y,batch_size=batch_size,
	epochs=epochs,
	verbose=1,
	validation_data=(X_test,test_y),
	shuffle=True)

# saving model
fer_json = model.to_json()
with open("fer.json","w") as json_file:
	json_file.write(fer_json)
model.save_weights("fer.h5")
