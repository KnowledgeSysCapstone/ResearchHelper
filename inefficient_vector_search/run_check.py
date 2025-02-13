import sys

import numpy as np

import argparse

parser = argparse.ArgumentParser(prog='ManualVectorSearch',
                                 description='Search for a sentence in a file of vectors by comparing similarity')
parser.add_argument('sentence_file', help="File with plaintext sentences on each line")
parser.add_argument('vectors_file', help="File to load vectors from")
parser.add_argument('sentence', help="Sentence to encode and use as a query")
parser.add_argument('--model', '-m', choices=['USE', 'SBERT'], default='USE', help="Language model to use for encoding query")

args = parser.parse_args()

sentence_idxs = None
similarities = None

if args.model == 'USE':

    import tensorflow as tf
    import tensorflow_hub as hub
    import tf_keras as keras

    embed = hub.load("https://www.kaggle.com/models/google/universal-sentence-encoder/TensorFlow2/large/2")

    embeddings = tf.convert_to_tensor(np.load(args.vectors_file), tf.float32)

    cos_sim = keras.losses.CosineSimilarity(axis=1, reduction='none')

    query = embed([args.sentence])
    similarities = cos_sim(embeddings, query)
    indices = tf.argsort(similarities)

    sentence_idxs = [int(x) for x in tf.unstack(indices)]
    sentence_idxs.reverse()

elif args.model == 'SBERT':
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer("all-MiniLM-L6-v2")

    embeddings = np.load(args.vectors_file)
    query = model.encode(args.sentence)

    similarities = model.similarity(embeddings, query)[:, 0]
    indices = np.argsort(similarities)
    sentence_idxs = indices

with open(args.sentence_file, 'r') as sentence_file:
    sentences = sentence_file.readlines()

for idx in sentence_idxs:
    print(float(similarities[idx]), sentences[idx].rstrip())
