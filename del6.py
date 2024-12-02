# -*- coding: utf-8 -*-
"""DEL5.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1hJSDMCqaeXaEBjXAGZXEBDoLo_O0US1q
"""

import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt


(x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data()
x_train, x_test = x_train / 255.0, x_test / 255.0
x_train, x_test = x_train[..., tf.newaxis], x_test[..., tf.newaxis]


def create_model():
    model = tf.keras.Sequential([
        tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(28, 28, 1)),
        tf.keras.layers.MaxPooling2D((2, 2)),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dense(10, activation='softmax')
    ])
    return model

model = create_model()


model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

@tf.function
def generate_adversarial_example(model, x, y, epsilon=0.1):
    with tf.GradientTape() as tape:
        tape.watch(x)
        predictions = model(x)
        loss = tf.keras.losses.sparse_categorical_crossentropy(y, predictions)
    gradients = tape.gradient(loss, x)
    adv_x = x + epsilon * tf.sign(gradients)
    return tf.clip_by_value(adv_x, 0.0, 1.0)


def compute_tangent_vectors(image, transforms=['rotate', 'translate']):
    vectors = []
    for transform in transforms:
        if transform == 'rotate':
            perturbed = tf.image.rot90(image, k=1)
        elif transform == 'translate':
            perturbed = tf.roll(image, shift=2, axis=0)
        tangent_vector = (perturbed - image).numpy().flatten()
        vectors.append(tangent_vector)
    return np.array(vectors)

def tangent_distance(image1, image2):
    tangent1 = compute_tangent_vectors(image1)
    tangent2 = compute_tangent_vectors(image2)
    diff = image1.numpy().flatten() - image2.numpy().flatten()
    tangent_matrix = np.vstack([tangent1, tangent2])
    pseudo_inverse = np.linalg.pinv(tangent_matrix.T @ tangent_matrix)
    projection = tangent_matrix.T @ pseudo_inverse @ tangent_matrix
    return np.linalg.norm(diff - projection @ diff)


@tf.function
def tangent_prop_loss(model, x, y, transform_fn, alpha=0.1):
    with tf.GradientTape() as tape:
        predictions = model(x)
        clean_loss = tf.keras.losses.sparse_categorical_crossentropy(y, predictions)
        perturbed_x = transform_fn(x)
        perturbed_predictions = model(perturbed_x)
        tangent_loss = alpha * tf.reduce_mean(tf.norm(predictions - perturbed_predictions, axis=1))
    total_loss = clean_loss + tangent_loss
    return total_loss


def transform_fn(images):
    return tf.image.random_flip_left_right(images)


@tf.function
@tf.function
def train_step(model, optimizer, x, y, epsilon=0.05, alpha=0.01):
    adv_x = generate_adversarial_example(model, x, y, epsilon)
    with tf.GradientTape() as tape:
        clean_predictions = model(x)
        adv_predictions = model(adv_x)
        adv_loss = tf.reduce_mean(tf.keras.losses.sparse_categorical_crossentropy(y, adv_predictions))
        tangent_loss = alpha * tf.reduce_mean(tf.square(clean_predictions - model(transform_fn(x))))
        total_loss = adv_loss + tangent_loss
    gradients = tape.gradient(total_loss, model.trainable_variables)


    clipped_gradients = [tf.clip_by_norm(g, 1.0) for g in gradients]
    optimizer.apply_gradients(zip(clipped_gradients, model.trainable_variables))

    return total_loss


epochs = 3
batch_size = 64
optimizer = tf.keras.optimizers.Adam()
train_dataset = tf.data.Dataset.from_tensor_slices((x_train, y_train)).shuffle(10000).batch(batch_size)

for epoch in range(epochs):
    print(f"Epoch {epoch + 1}/{epochs}")
    for step, (x_batch, y_batch) in enumerate(train_dataset):
        loss = train_step(model, optimizer, x_batch, y_batch, epsilon=0.1, alpha=0.1)
        if step % 100 == 0:
            print(f"Step {step}, Loss: {loss.numpy():.4f}")


test_loss, test_acc = model.evaluate(x_test, y_test, verbose=2)
print(f"Test accuracy: {test_acc:.4f}")
