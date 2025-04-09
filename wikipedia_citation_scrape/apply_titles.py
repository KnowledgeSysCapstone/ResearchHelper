import json
import re
import requests
from sentence_transformers import SentenceTransformer


def crossref_title(doi: str) -> str:
    metadata = requests.get("https://api.crossref.org/works/{}".format(doi))
    if metadata.text == "Resource not found.":
        return "> No Resource"
    metadata_dict = json.loads(metadata.text)["message"]
    if "title" not in metadata_dict:
        # print(json.dumps(metadata_dict, indent=2))
        #print("NON", doi)
        return "> No Title"
    else:
        title = metadata_dict["title"][0]
        title = re.sub("<(.*?)>", "", title)

        return title


with open("abstracts_full.txt", 'r', encoding='UTF-8') as ffile, \
        open("abstracts_sentenced.txt", 'r', encoding='UTF-8') as sfile, \
        open("abstracts_title.txt", 'w', encoding='UTF-8') as tfile, \
        open("abstracts_titlefull.txt", 'w', encoding='UTF-8') as tffile, \
        open("abstracts_titlesentenced.txt", 'w', encoding='UTF-8') as tsfile:
    abstracts = json.load(ffile)
    sentences = json.load(sfile)
    titles = {}
    t_and_f = {}
    t_and_s = {}
    for i, doi in enumerate(abstracts):
        title = crossref_title(doi)
        # print(title)
        # print(abstracts[doi][0])
        titles[doi] = [title]
        print(f"{i+1} out of {len(abstracts)}")

        t_and_f[doi] = [title + ": " + a for a in abstracts[doi]]

        t_and_s[doi] = [title + ": " + s for s in sentences[doi]]


    json.dump(titles, tfile, indent=2)
    json.dump(t_and_f, tffile, indent=2)
    json.dump(t_and_s, tsfile, indent=2)


model = SentenceTransformer("all-MiniLM-L6-v2")
vector_dict = {}

with open('abstracts_title.txt', 'r', encoding='UTF-8') as tfile, \
    open('abstracts_titlefull.txt', 'r', encoding='UTF-8') as tffile, \
    open('abstracts_titlesentenced.txt', 'r', encoding='UTF-8') as tsfile:

    titles = json.load(tfile)
    titlefulls = json.load(tffile)
    titlesentenceds = json.load(tsfile)

data_stores = {
    # "full": abstracts,
    # "sentenced": processed
    "title": titles,
    "titlefull": titlefulls,
    "titlesentenced": titlesentenceds
}

for ds in data_stores:

    sentence_dict = data_stores[ds]

    tot = len(sentence_dict)
    i = 0
    for doi in sentence_dict:
        sentences = sentence_dict[doi]

        # if ds == 'sentenced':
        #     vector_dict[doi] = prev_vects[doi]
        # else:
        embeddings = model.encode(sentences)
        vector_dict[doi] = embeddings.tolist()

        print(f"task {ds} article {doi}: {i + 1}/{tot}")
        i += 1

    json_str = json.dumps(vector_dict, indent=2)
    json_str = json_str.replace("\n      ", "")
    json_str = json_str.replace("\n      ", "")
    json_str = json_str.replace("\n    ]", "]")

    with open(f'abstracts_{ds}_vectorized.txt', 'w', encoding='UTF-8') as file:
        file.write(json_str)
