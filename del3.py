# -*- coding: utf-8 -*-
"""DEL3.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1TpU_AKH9W09bc9rvggDQbI1Jwt8OJtkQ

###Multi-Layer Perceptron with non-linear activation function that solves XOR Problem
"""

import numpy as np

input_size = 2
layers = [4]
output_size = 1

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

def sigmoid_derivative(x):
    return x * (1 - x)

class NeuralNetwork:
    def __init__(self, input_size, layers, output_size):
        np.random.seed(0)

        self.model = {
            'w1': np.random.randn(input_size, layers[0]),
            'b1': np.zeros((1, layers[0])),
            'w2': np.random.randn(layers[0], output_size),
            'b2': np.zeros((1, output_size))
        }

    def forward(self, x):
        self.z1 = np.dot(x, self.model['w1']) + self.model['b1']
        self.a1 = sigmoid(self.z1)
        self.z2 = np.dot(self.a1, self.model['w2']) + self.model['b2']
        output = sigmoid(self.z2)
        return output

    def backward(self, x, y, learning_rate=0.1):
        m = y.shape[0]
        output = self.forward(x)

        output_loss = output - y
        dw2 = np.dot(self.a1.T, output_loss) / m
        db2 = np.sum(output_loss, axis=0) / m

        hidden_loss = np.dot(output_loss, self.model['w2'].T) * sigmoid_derivative(self.a1)
        dw1 = np.dot(x.T, hidden_loss) / m
        db1 = np.sum(hidden_loss, axis=0) / m

        self.model['w1'] -= learning_rate * dw1
        self.model['b1'] -= learning_rate * db1
        self.model['w2'] -= learning_rate * dw2
        self.model['b2'] -= learning_rate * db2

    def predict(self, x):
        output = self.forward(x)
        return np.round(output)

X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
Y = np.array([[0], [1], [1], [0]])


model = NeuralNetwork(input_size=2, layers=[4], output_size=1)

def train(x, y, model, epochs):
    for epoch in range(epochs):
        model.backward(x, y)


train(X, Y, model, epochs=5000)

predictions = model.predict(X)
print("Predictions:")
print(predictions)
print("True Labels:")
print(Y)

"""###Multi-class classification using softmax activation function, for iris data

"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import confusion_matrix


iris = load_iris()
X = iris.data
y = iris.target.reshape(-1, 1)


encoder = OneHotEncoder(sparse_output=False)
y_enc = encoder.fit_transform(y)


X_train, X_test, y_train, y_test = train_test_split(X, y_enc, test_size=0.2, random_state=42)


scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

def softmax(x):
    exp_x = np.exp(x - np.max(x))
    return exp_x / np.sum(exp_x, axis=1, keepdims=True)


class NeuralNetwork:
    def __init__(self, input_size, hidden_size, output_size):
        np.random.seed(0)
        self.model = {
            'w1': np.random.randn(input_size, hidden_size),
            'b1': np.zeros((1, hidden_size)),
            'w2': np.random.randn(hidden_size, output_size),
            'b2': np.zeros((1, output_size))
        }

    def forward(self, x):
        self.z1 = np.dot(x, self.model['w1']) + self.model['b1']
        self.a1 = np.maximum(0, self.z1)
        self.z2 = np.dot(self.a1, self.model['w2']) + self.model['b2']
        output = softmax(self.z2)
        return output

    def backward(self, x, y, learning_rate=0.001):
        m = y.shape[0]
        output = self.forward(x)


        output_loss = output - y
        dw2 = np.dot(self.a1.T, output_loss) / m
        db2 = np.sum(output_loss, axis=0) / m


        hidden_loss = np.dot(output_loss, self.model['w2'].T) * (self.a1 > 0)
        dw1 = np.dot(x.T, hidden_loss) / m
        db1 = np.sum(hidden_loss, axis=0) / m


        self.model['w1'] -= learning_rate * dw1
        self.model['b1'] -= learning_rate * db1
        self.model['w2'] -= learning_rate * dw2
        self.model['b2'] -= learning_rate * db2

    def predict(self, x):
        output = self.forward(x)
        return np.argmax(output, axis=1)


input_size = X.shape[1]
hidden_size = 5
output_size = y_enc.shape[1]

model = NeuralNetwork(input_size, hidden_size, output_size)


for epoch in range(300):
    model.backward(X_train, y_train, learning_rate=0.01)


predictions = model.predict(X_test)
true_classes = np.argmax(y_test, axis=1)
accuracy = np.mean(predictions == true_classes)
print(f'Accuracy: {accuracy * 100:.2f}%')



conf_matrix = confusion_matrix(true_classes, predictions)
plt.subplot(1, 2, 2)
sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues', xticklabels=encoder.categories_[0], yticklabels=encoder.categories_[0])
plt.xlabel('Predicted Class')
plt.ylabel('True Class')
plt.title('Confusion Matrix')

plt.tight_layout()
plt.show()

