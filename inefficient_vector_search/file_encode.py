import tensorflow_hub as hub
import tensorflow as tf
import numpy as np

embed = hub.load("https://www.kaggle.com/models/google/universal-sentence-encoder/TensorFlow2/large/2")

with open("Hot_dog_sentences.txt", 'r') as in_file:
    items = in_file.readlines()

embeddings = embed(items)

np.save("Hot_dog_encodings", embeddings)

#emb_str = tf.strings.format("{}", embeddings, summarize=-1)
#tf.io.write_file("Hot_dog_encodings.txt", emb_str)

print(embeddings)

# with open("Hot_dog_encodings.txt", 'w') as out_file:
#      json.dump(out_file, embeddings)
