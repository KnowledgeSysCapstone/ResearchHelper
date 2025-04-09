import spacy
import json

from sentence_transformers import SentenceTransformer

if __name__ == '__main__':

    with open('rawtext_dataset.txt', 'r', encoding='UTF-8') as infile:
        dataset = json.load(infile)
    abstracts = {}

    for i, x in enumerate(dataset):
        if x['abstract'][0] != '>' and x['doi'] not in abstracts and len(x['abstract']) >= 50:
            abstracts[x['doi']] = [x['abstract']]

    with open('abstracts_full.txt', 'w', encoding='UTF-8') as outfile:
        json.dump(abstracts, outfile, indent=2)

    # Separate into sentences
    # nlp = spacy.load("en_core_web_trf")

    with open('abstracts_parsed.txt', 'r', encoding='UTF-8') as prev_sent_file:
        prev_sents = json.load(prev_sent_file)

    tot = len(abstracts)
    processed = {}
    for i, x in enumerate(abstracts):
        print(f"{i+1} / {tot} processed")

        # doc = nlp(abstracts[x][0])
        # sentences = [sent.text.strip() for sent in doc.sents]
        # processed[x] = [s for s in sentences if len(s) > 0]

        processed[x] = prev_sents[x]

    with open('abstracts_sentenced.txt', 'w', encoding='UTF-8') as file:
        json.dump(processed, file, indent=2)


    # with open('abstracts_parsed.txt', 'r', encoding='UTF-8') as file:
    #     sentence_dict = json.load(file)
    #
    model = SentenceTransformer("all-MiniLM-L6-v2")
    vector_dict = {}


    data_stores = {
        "full": abstracts,
        "sentenced": processed
    }

    with open('abstracts_vectorized.txt', 'r', encoding='UTF-8') as prev_vect_file:
        prev_vects = json.load(prev_vect_file)

    for ds in data_stores:

        sentence_dict = data_stores[ds]

        tot = len(sentence_dict)
        i = 0
        for doi in sentence_dict:
            sentences = sentence_dict[doi]

            if ds == 'sentenced':
                vector_dict[doi] = prev_vects[doi]
            else:
                embeddings = model.encode(sentences)
                vector_dict[doi] = embeddings.tolist()

            print(f"task {ds} article {doi}: {i+1}/{tot}")
            i += 1

        json_str = json.dumps(vector_dict, indent=2)
        json_str = json_str.replace("\n      ", "")
        json_str = json_str.replace("\n      ", "")
        json_str = json_str.replace("\n    ]", "]")

        with open(f'abstracts_{ds}_vectorized.txt', 'w', encoding='UTF-8') as file:
            file.write(json_str)
