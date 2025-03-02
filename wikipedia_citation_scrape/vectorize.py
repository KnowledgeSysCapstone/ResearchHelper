import spacy
import json


if __name__ == '__main__':
    nlp = spacy.load("en_core_web_trf")

    with open('rawtext_dataset.txt', 'r', encoding='UTF-8') as file:
        dataset = json.load(file)
    processed = {}

    tot = len(dataset)

    for i, x in enumerate(dataset):
        print(f"{i} / {tot} processed")
        if x['abstract'][0] != '>' and x['doi'] not in processed:

            doc = nlp(x['abstract'])
            #assert doc.has_annotation("SENT_START")
            sentences = [sent.text.strip() for sent in doc.sents]
            processed[x['doi']] = [s for s in sentences if len(s)>0]

    with open('abstracts_parsed.txt', 'w', encoding='UTF-8') as file:
        json.dump(processed, file, indent=2)
