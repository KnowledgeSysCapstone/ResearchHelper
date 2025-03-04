import spacy
import json

from sentence_transformers import SentenceTransformer

if __name__ == '__main__':


    # Separate into sentences
    # nlp = spacy.load("en_core_web_trf")
    #
    # with open('rawtext_dataset.txt', 'r', encoding='UTF-8') as file:
    #     dataset = json.load(file)
    # processed = {}
    #
    # tot = len(dataset)
    #
    # for i, x in enumerate(dataset):
    #     print(f"{i} / {tot} processed")
    #     if x['abstract'][0] != '>' and x['doi'] not in processed:
    #
    #         doc = nlp(x['abstract'])
    #         #assert doc.has_annotation("SENT_START")
    #         sentences = [sent.text.strip() for sent in doc.sents]
    #         processed[x['doi']] = [s for s in sentences if len(s)>0]
    #
    # with open('abstracts_parsed.txt', 'w', encoding='UTF-8') as file:
    #     json.dump(processed, file, indent=2)

    with open('abstracts_parsed.txt', 'r', encoding='UTF-8') as file:
        sentence_dict = json.load(file)

    model = SentenceTransformer("all-MiniLM-L6-v2")
    vector_dict = {}

    tot = len(sentence_dict)
    i = 0
    for doi in sentence_dict:
        sentences = sentence_dict[doi]

        embeddings = model.encode(sentences)

        vector_dict[doi] = embeddings.tolist()
        print(f"article {doi}: {i}/{tot}")
        i += 1

    json_str = json.dumps(vector_dict, indent=2)
    json_str = json_str.replace("\n      ", "")
    json_str = json_str.replace("\n      ", "")
    json_str = json_str.replace("\n    ]", "]")

    with open('abstracts_vectorized.txt', 'w', encoding='UTF-8') as file:
        file.write(json_str)
