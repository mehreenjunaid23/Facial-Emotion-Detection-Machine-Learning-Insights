# -*- coding: utf-8 -*-
"""Emotion_classification_Ml_project.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1lfipBIbzMbWyWXQSk1n5A1RuWPPm1U63
"""

from google.colab import drive
drive.mount('/content/drive')

import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.optimizers import RMSprop
import matplotlib.pyplot as plt
import numpy as np
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from tensorflow.keras.applications import VGG16
from sklearn.metrics import classification_report, confusion_matrix

# Set the path to the dataset folder
train_dir = '/content/drive/MyDrive/data/train'
test_dir = '/content/drive/MyDrive/test'

# Set the parameters for the CNN model
img_width, img_height = 48, 48
batch_size = 40
epochs = 40

# Define the data generators for the training and testing sets
train_datagen = ImageDataGenerator(rescale=1./255,
                                   rotation_range=30,
                                   shear_range=0.3,
                                   zoom_range=0.3,
                                   horizontal_flip=True,
                                   fill_mode='nearest')
test_datagen = ImageDataGenerator(rescale=1./255)

train_generator = train_datagen.flow_from_directory(train_dir,
                                                    target_size=(img_width, img_height),
                                                    batch_size=batch_size,
                                                    class_mode='categorical')
test_generator = test_datagen.flow_from_directory(test_dir,
                                                  target_size=(img_width, img_height),
                                                  batch_size=batch_size,
                                                  class_mode='categorical',
                                                  shuffle=False)

# Calculate the class weights for the training set
class_weights = dict(zip(range(7), [1] * 7))  # Equal weights for all classes

# Build the CNN model
model = Sequential()
model.add(Conv2D(32, (3, 3), activation='relu', input_shape=(img_width, img_height, 3)))
model.add(MaxPooling2D((2, 2)))
model.add(Conv2D(64, (3, 3), activation='relu'))
model.add(MaxPooling2D((2, 2)))
model.add(Conv2D(128, (3, 3), activation='relu'))
model.add(MaxPooling2D((2, 2)))
model.add(Flatten())
model.add(Dense(128, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(7, activation='softmax'))

model.summary()

# Compile the model
model.compile(loss='categorical_crossentropy',
              optimizer=RMSprop(learning_rate=1e-4),
              metrics=['accuracy'])

# Train the model on the training set
history = model.fit(train_generator,
                    steps_per_epoch=train_generator.samples // batch_size,
                    epochs=epochs,
                    class_weight=class_weights) # Pass the class weights to fit()

# Predict the test data
test_generator.reset() # Resets the generator to the beginning
predictions = model.predict(test_generator)
predicted_classes = np.argmax(predictions, axis=1)

# Display the prediction vs actual graph
true_classes = test_generator.classes
class_labels = list(test_generator.class_indices.keys())

plt.figure(figsize=(7, 7))
plt.subplots_adjust(wspace=0.5)

plt.subplot(1, 2, 1)
plt.plot(history.history['loss'], label='Training Loss')
plt.plot(history.history['accuracy'], label='Training Accuracy')
plt.xlabel('Epoch')
plt.ylabel('Loss/Accuracy')
plt.title('Training Loss and Accuracy')
plt.legend()

plt.subplot(1, 2, 2)
plt.hist2d(true_classes, predicted_classes, bins=(len(class_labels), len(class_labels)), cmap=plt.cm.Blues)
plt.colorbar()
plt.xticks(range(len(class_labels)), class_labels, rotation=90)
plt.yticks(range(len(class_labels)), class_labels)
plt.xlabel('True Class')
plt.ylabel('Predicted Class')
plt.title('Confusion Matrix')

plt.show()

# Evaluate the model on the test set (additional)
test_loss, test_accuracy = model.evaluate(test_generator)

# Calculate additional evaluation metrics
test_predictions = model.predict(test_generator)
test_predicted_classes = np.argmax(test_predictions, axis=1)
test_true_classes = test_generator.classes

test_report = classification_report(test_true_classes, test_predicted_classes, target_names=class_labels)
test_confusion = confusion_matrix(test_true_classes, test_predicted_classes)

# Print the metrics
print(f"Test Loss: {test_loss:.4f}")
print(f"Test Accuracy: {test_accuracy:.4f}")
print("Test Report:")
print(test_report)
print("Test Confusion Matrix:")
print(test_confusion)

# Evaluate the model on the test set
_, accuracy = model.evaluate(test_generator)
print(f"CNN accuracy: {accuracy*100:.2f}%")

# Compare to SVM
train_data = train_generator.next()[0]
train_labels = np.argmax(train_generator.next()[1], axis=1)
test_data = test_generator.next()[0]
test_labels = np.argmax(test_generator.next()[1], axis=1)
svm = SVC(kernel='linear', C=0.1, gamma='auto')
svm.fit(train_data.reshape(train_data.shape[0], -1), train_labels)
svm_accuracy = svm.score(test_data.reshape(test_data.shape[0], -1), test_labels)
print(f"SVM accuracy: {svm_accuracy*100:.2f}%")

# Compare to Decision Tree
dt = DecisionTreeClassifier(max_depth=10)
dt.fit(train_data.reshape(train_data.shape[0], -1), train_labels)
dt_accuracy = dt.score(test_data.reshape(test_data.shape[0], -1), test_labels)
print(f"Decision Tree accuracy: {dt_accuracy*100:.2f}%")