from rank_bm25 import BM25Okapi
import json
import numpy as np

with open("abstracts_full.txt", 'r', encoding='UTF-8') as file:
    abstracts = json.load(file)

dois = [x for x in abstracts.keys()]
corpus = [abstracts[d][0] for d in dois]


tokenized_corpus = [doc.split(" ") for doc in corpus]

bm25 = BM25Okapi(tokenized_corpus)
print("corpus evaluated")

with open("queries.txt", 'r', encoding='UTF-8') as qfile:
    queries = json.load(qfile)

rec_results = {}
all_indices = []
for q in queries:
    qtext = queries[q]['text']
    tokenized_query = qtext.split(" ")
    doc_scores = bm25.get_scores(tokenized_query)
    all_indices.append(np.argsort(-doc_scores))

    res_dict = {}
    res_dict["text"] = queries[q]["text"]
    res_dict["relevant"] = queries[q]["dois"]
    rec_results[int(q)] = res_dict

    print(f"{int(q)+1}/{len(queries)} queries tested")

final_dict = {"n_claims": len(queries), "n_docs": len(corpus)}

MATCH_NUMS = [5]
max_match = max(MATCH_NUMS)
for match in MATCH_NUMS:
    mean_avgprec = 0
    for q, top_results in enumerate(all_indices):
        res_dict = rec_results[q]

        if "received" not in res_dict:
            received = []
            for c in top_results:
                #print(similarities[q][c])
                if dois[c] not in received:
                    received.append(dois[c])
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

        avgprec /= len(res_dict["relevant"])

        res_dict[f"avep@{match}"] = avgprec
        mean_avgprec += avgprec

        print(f"avep@{match} for {q+1}/{len(all_indices)}")

    mean_avgprec /= len(all_indices)

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

with open(f"MATCH_for_bm25.txt", 'w', encoding="UTF-8") as matchf:
    json.dump(final_dict, matchf, indent=2)
