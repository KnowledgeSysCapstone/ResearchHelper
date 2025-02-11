import sys

import tensorflow as tf
import tensorflow_hub as hub
import tf_keras as keras
import numpy as np

embed = hub.load("https://www.kaggle.com/models/google/universal-sentence-encoder/TensorFlow2/large/2")

# string_tensor = tf.io.read_file("Hot_dog_encodings.txt")
embeddings = tf.convert_to_tensor(np.load("Hot_dog_encodings.npy"), tf.float32)

cos_sim = keras.losses.CosineSimilarity(axis=1, reduction='none')

if __name__ == '__main__':
    sentence = sys.argv[1]
    query = embed([sentence])
    similarities = cos_sim(embeddings, query)
    indices = tf.argsort(similarities)

    with open("Hot_dog_sentences.txt", 'r') as sentence_file:
        sentences = sentence_file.readlines()

    for x in tf.unstack(indices):
        idx = int(x)
        print(float(similarities[idx]), sentences[idx].rstrip())


