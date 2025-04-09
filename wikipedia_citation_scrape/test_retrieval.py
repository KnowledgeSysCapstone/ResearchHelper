import json
import numpy as np
import sklearn

task = "titlesentenced"

with open(f"abstracts_{task}_vectorized.txt", 'r', encoding='UTF-8') as afile:
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

rec_results = {}
for q, top_results in enumerate(indices):
    res_dict = {}
    res_dict["text"] = queries[str(q)]["text"]
    res_dict["relevant"] = queries[str(q)]["dois"]
    rec_results[q] = res_dict

final_dict = {"n_claims": len(all_queries), "n_docs": len(all_doi)}

MATCH_NUMS = [5]
max_match = max(MATCH_NUMS)
for match in MATCH_NUMS:
    mean_avgprec = 0
    for q, top_results in enumerate(indices):
        res_dict = rec_results[q]

        if "received" not in res_dict:
            received = []
            for c in top_results:
                #print(similarities[q][c])
                if all_doi[c] not in received:
                    received.append(all_doi[c])
                if len(received) >= max_match:
                    break
            res_dict["received"] = received

        avgprec = 0
        valid_sofar = 0
        for i, t in enumerate(res_dict["received"]):
            if i >= match:
                break
            if t in res_dict["relevant"]:
                valid_sofar += 1
                avgprec += valid_sofar / (i+1)
                # print(q, i)

        avgprec /= len(res_dict["relevant"])

        res_dict[f"avep@{match}"] = avgprec
        mean_avgprec += avgprec

    #
    # q_e = np.array([queries[str(q)]["vector"]])
    # a_e = np.array(abstracts[queries[str(q)]["dois"][0]])
    # f_e = np.array(abstracts[received[0]])
    # print(sklearn.metrics.pairwise.cosine_similarity(q_e, a_e))
    # print(sklearn.metrics.pairwise.cosine_similarity(q_e, f_e))
    # print([similarities[q][c] for c in range(len(all_doi)) if all_doi[c] == queries[str(q)]["dois"][0]])
    # print("---")

    mean_avgprec /= indices.shape[0]

    final_dict[f"map@{match}"] = mean_avgprec

TOP_NUMS = [1]
for top in TOP_NUMS:
    count_top = 0
    for r in rec_results:
        rec_results[r][f"any@{top}"] = False
        for relevant in rec_results[r]["relevant"]:
            if relevant in rec_results[r]["received"][:top]:
                count_top += 1
                rec_results[r][f"any@{top}"] = True
                break
    final_dict[f"countany@{top}"] = count_top / len(rec_results)

final_dict["query_results"] = rec_results

with open(f"MATCH_for_{task}.txt", 'w', encoding="UTF-8") as matchf:
    json.dump(final_dict, matchf, indent=2)


