import json

with open("rawtext_dataset.txt", 'r', encoding='UTF-8') as file:
    rtds = json.load(file)


query_as_key = {}
dontallow = ["|", "{", "}", "http"]
for x in rtds:
    sentence = x["wiki_sentence"]

    if len(sentence) < 75 or len(sentence) > 175:
        continue

    for d in dontallow:
        if d in sentence:
            continue

    if sentence not in query_as_key:
        query_as_key[sentence] = [x["doi"]]
    else:
        query_as_key[sentence].append(x["doi"])


from sentence_transformers import SentenceTransformer
model = SentenceTransformer("all-MiniLM-L6-v2")

idx_as_key = {}
for i, query in enumerate(query_as_key.keys()):

    print(f"on {i+1} / {len(query_as_key)}")

    qdict = {}
    qdict["text"] = query
    qdict["dois"] = query_as_key[query]

    embeddings = model.encode(query)

    qdict["vector"] = embeddings.tolist()

    idx_as_key[i] = qdict

with open("queries.txt", 'w', encoding='UTF-8') as qfile:
    json.dump(idx_as_key, qfile, indent=2)
