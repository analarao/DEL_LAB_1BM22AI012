# -*- coding: utf-8 -*-
"""DEL5.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1zJ2NWv-lpUsyr3uoegVRDEOtoSHOAjPW
"""

import tensorflow as tf
from tensorflow.keras.layers import Dense, Input, Flatten
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.datasets import mnist, fashion_mnist

# Load two datasets: MNIST and Fashion MNIST (for simplicity in demonstration)
(x1_train, y1_train), (x1_test, y1_test) = mnist.load_data()
(x2_train, y2_train), (x2_test, y2_test) = fashion_mnist.load_data()

# Normalize datasets
x1_train, x1_test = x1_train / 255.0, x1_test / 255.0
x2_train, x2_test = x2_train / 255.0, x2_test / 255.0

# Expand dimensions for channel consistency
x1_train, x1_test = x1_train[..., tf.newaxis], x1_test[..., tf.newaxis]
x2_train, x2_test = x2_train[..., tf.newaxis], x2_test[..., tf.newaxis]

# Shared input layer
input_layer = Input(shape=(28, 28, 1), name="shared_input")

# Shared feature extractor
shared = Flatten()(input_layer)
shared = Dense(128, activation='relu')(shared)
shared = Dense(64, activation='relu')(shared)

# Task-specific output heads
task1_output = Dense(10, activation='softmax', name="task1")(shared)  # MNIST classification
task2_output = Dense(10, activation='softmax', name="task2")(shared)  # Fashion MNIST classification

# Create multi-task model
model = Model(inputs=input_layer, outputs=[task1_output, task2_output])

# Compile the model
model.compile(
    optimizer=Adam(learning_rate=0.001),
    loss={
        "task1": "sparse_categorical_crossentropy",
        "task2": "sparse_categorical_crossentropy",
    },
    metrics={
        "task1": "accuracy",
        "task2": "accuracy",
    }
)

# Early stopping callback
early_stopping = EarlyStopping(
    monitor="val_loss",  # Monitor combined validation loss of all tasks
    patience=3,
    restore_best_weights=True,
    verbose=1
)

# Train the model
history = model.fit(
    x1_train,  # Input is shared for both tasks
    {"task1": y1_train, "task2": y2_train},  # Output labels for each task
    validation_data=(
        x1_test,  # Validation input is shared
        {"task1": y1_test, "task2": y2_test}  # Validation labels for each task
    ),
    batch_size=64,
    epochs=20,
    callbacks=[early_stopping]
)

# Evaluate the model on test data
results = model.evaluate(
    x1_test,  # Test input
    {"task1": y1_test, "task2": y2_test},  # Test labels for both tasks
    verbose=2
)

# Print evaluation results
print(f"Test Results:\nTask1 (MNIST): Loss = {results[1]:.4f}, Accuracy = {results[3]:.4f}")
print(f"Task2 (Fashion MNIST): Loss = {results[2]:.4f}, Accuracy = {results[4]:.4f}")

""