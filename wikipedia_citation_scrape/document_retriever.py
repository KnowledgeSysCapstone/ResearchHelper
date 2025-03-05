import json


def get_document():

    document_list = []

    with open("abstracts_parsed.txt", 'r', encoding='UTF-8') as sentence_file, \
        open("abstracts_vectorized.txt", 'r', encoding='UTF-8') as vector_file, \
        open("rawtext_dataset.txt", 'r', encoding='UTF-8') as raw_file:

        sentence_dict = json.load(sentence_file)
        vector_dict = json.load(vector_file)
        raw_list = json.load(raw_file)

        abstracts_dict = {}

        for r in raw_list:
            if r["doi"] not in abstracts_dict:
                abstracts_dict[r["doi"]] = r["abstract"]

        for doi in vector_dict:
            sentence_pairs = []
            for s in range(len(vector_dict[doi])):
                sub_dict = {
                    "text": sentence_dict[doi][s],
                    "vector": vector_dict[doi][s]
                }
                sentence_pairs.append(sub_dict)

            document = {
                "doi": doi,
                "abstract": abstracts_dict[doi],
                "sentences": sentence_pairs
            }

            document_list.append(document)

    return document_list


if __name__ == '__main__':
    print(json.dumps(get_document()[0], indent=2))

