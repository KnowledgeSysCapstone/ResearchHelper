import json
import numpy as np
import sklearn

with open("abstracts_vectorized.txt", 'r', encoding='UTF-8') as afile:
    abstracts = json.load(afile)

all_doi = []
all_vectors = []
for doi in abstracts:
    for vector in abstracts[doi]:
        all_doi.append(doi)
        all_vectors.append(vector)

abstract_embed = np.array(all_vectors)

with open("queries.txt", 'r', encoding='UTF-8') as qfile:
    queries = json.load(qfile)

all_queries = []
for q in sorted((int(x) for x in queries.keys())):
    all_queries.append(queries[str(q)]["vector"])

query_embed = np.array(all_queries)

print("a_e", abstract_embed.shape)
print("q_e", query_embed.shape)
similarities = sklearn.metrics.pairwise.cosine_similarity(query_embed, abstract_embed)
print("sim", similarities.shape)
indices = np.argsort(-similarities, axis=-1)
print("ind", indices.shape)



MATCH_NUM = 5
rec_results = {}
mean_avgprec = 0
for q, top_results in enumerate(indices):
    res_dict = {}
    res_dict["text"] = queries[str(q)]["text"]
    res_dict["relevant"] = queries[str(q)]["dois"]
    received = []
    for c in top_results:
        #print(similarities[q][c])
        if all_doi[c] not in received:
            received.append(all_doi[c])
        if len(received) >= MATCH_NUM:
            break
    res_dict["received"] = received

    avgprec = 0
    valid_sofar = 0
    for i, t in enumerate(res_dict["received"]):
        if t in res_dict["relevant"]:
            valid_sofar += 1
            avgprec += valid_sofar / (i+1)

            print(q, i)

    avgprec /= len(res_dict["relevant"])

    res_dict[f"avep@{MATCH_NUM}"] = avgprec
    mean_avgprec += avgprec

    rec_results[q] = res_dict

    #
    # q_e = np.array([queries[str(q)]["vector"]])
    # a_e = np.array(abstracts[queries[str(q)]["dois"][0]])
    # f_e = np.array(abstracts[received[0]])
    # print(sklearn.metrics.pairwise.cosine_similarity(q_e, a_e))
    # print(sklearn.metrics.pairwise.cosine_similarity(q_e, f_e))
    # print([similarities[q][c] for c in range(len(all_doi)) if all_doi[c] == queries[str(q)]["dois"][0]])
    # print("---")

mean_avgprec /= indices.shape[0]

with open("MATCH_per_sentence.txt", 'w', encoding="UTF-8") as matchf:
    json.dump({f"map@{MATCH_NUM}": mean_avgprec, "query_results": rec_results}, matchf, indent=2)


