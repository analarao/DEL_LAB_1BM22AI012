# -*- coding: utf-8 -*-
"""DEL4.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1rbrUKLfoQflrtrXpgnEytqKJsoUmeR5I
"""

import numpy as np
import pandas as pd
from sklearn.datasets import load_iris
from sklearn.preprocessing import OneHotEncoder
from sklearn.model_selection import train_test_split

iris = load_iris()
X = iris.data
y = iris.target.reshape(-1, 1)

encoder = OneHotEncoder(sparse_output=False)
y_encoded = encoder.fit_transform(y)

X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

def sigmoid_derivative(x):
    return x * (1 - x)

input_size = X_train.shape[1]
hidden_size = 5
output_size = y_encoded.shape[1]

np.random.seed(42)

w1 = np.random.rand(input_size, hidden_size)
b1 = np.random.rand(hidden_size)

w2 = np.random.rand(hidden_size, output_size)
b2 = np.random.rand(output_size)

def forward_pass(X):
    hidden_input = np.dot(X, w1) + b1
    hidden_output = sigmoid(hidden_input)
    output_input = np.dot(hidden_output, w2) + b2
    output = sigmoid(output_input)
    return hidden_output, output

def backward_pass(X, y, hidden_output, output, learning_rate):
    global w1, b1, w2, b2

    output_error = y - output
    output_delta = output_error * sigmoid_derivative(output)

    hidden_error = output_delta.dot(w2.T)
    hidden_delta = hidden_error * sigmoid_derivative(hidden_output)

    w2 += hidden_output.T.dot(output_delta) * learning_rate
    b2 += np.sum(output_delta, axis=0) * learning_rate

    w1 += X.T.dot(hidden_delta) * learning_rate
    b1 += np.sum(hidden_delta, axis=0) * learning_rate

def train(X, y, epochs, learning_rate):
    for epoch in range(epochs):
        hidden_output, output = forward_pass(X)
        backward_pass(X, y, hidden_output, output, learning_rate)
        if epoch % 100 == 0:
            loss = np.mean((y - output) ** 2)
            print(f'GD Epoch {epoch}, Loss: {loss}')

def train_sgd(X, y, epochs, learning_rate):
    for epoch in range(epochs):
        for i in range(len(X)):
            single_X = X[i:i+1]
            single_y = y[i:i+1]
            hidden_output, output = forward_pass(single_X)
            backward_pass(single_X, single_y, hidden_output, output, learning_rate)

        if epoch % 100 == 0:
            loss = np.mean((y - forward_pass(X)[1]) ** 2)
            print(f'SGD Epoch {epoch}, Loss: {loss}')

print("Training with Gradient Descent:")
train(X_train, y_train, epochs=1000, learning_rate=0.1)

weights_input_hidden = np.random.rand(input_size, hidden_size)
bias_hidden = np.random.rand(hidden_size)
weights_hidden_output = np.random.rand(hidden_size, output_size)
bias_output = np.random.rand(output_size)

print("\nTraining with Stochastic Gradient Descent:")
train_sgd(X_train, y_train, epochs=1000, learning_rate=0.1)
