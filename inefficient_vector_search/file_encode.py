
import numpy as np
import argparse

parser = argparse.ArgumentParser(prog='VectorEncoder',
                                 description='Encode a file of sentences into a list of vectors and save them')
parser.add_argument('sentence_file', help="File with plaintext sentences on each line")
parser.add_argument('vectors_file', help="Path to save list of vectors to")
parser.add_argument('--model', '-m', choices=['USE', 'SBERT'], default='USE', help="Language model to use for encodings")

args = parser.parse_args()

with open(args.sentence_file, 'r') as in_file:
    items = in_file.readlines()

if args.model == 'USE':

    import tensorflow_hub as hub

    embed = hub.load("https://www.kaggle.com/models/google/universal-sentence-encoder/TensorFlow2/large/2")
    embeddings = embed(items)

    np.save(args.vectors_file, embeddings)

elif args.model == 'SBERT':

    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(items)

    np.save(args.vectors_file, embeddings)

