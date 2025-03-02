import requests
import xml.etree.ElementTree as ET
import re
import json


def dump_contents(articles: list[str]) -> str:
    reqs = [requests.get("https://en.wikipedia.org/wiki/Special:Export/{}".format(p)) for p in articles]
    xmls = [r.text for r in reqs]
    ns = {"d": "http://www.mediawiki.org/xml/export-0.11/"}
    texts = []
    for x in xmls:
        root = ET.fromstring(x)
        elem = root.find("d:page/d:revision/d:text", ns)
        if elem is None:
            print(articles[0])
        texts.append(elem.text)

    fulltext = "\n\n".join(t for t in texts)
    return fulltext


def articles_from_bullets(fulltext: str) -> set[str]:
    articles_list = set()
    lines = fulltext.split("\n")
    for line in lines:
        if len(line) > 3 and line[0:2] == "* ":
            res = re.findall(r"\[\[(.*?)\]\]", line)
            cleaned = [x.split("|")[0].split("#")[0] for x in res]
            first_letter_fix = [x[0].capitalize() + x[1:] for x in cleaned]
            for x in first_letter_fix:
                print(x)
                if ':' in x and ' ' not in x.split(':')[0]:
                    continue

                redirect_check = requests.get(
                    r'https://en.wikipedia.org/w/api.php?action=query&titles={}&redirects&format=json'.format(x))

                data = json.loads(redirect_check.text)
                if 'redirects' in data['query']:
                    articles_list.add(data['query']['redirects'][0]['to'])
                else:
                    articles_list.add(x)

    return articles_list


def all_dois(article_text: str) -> list[tuple[str, int]]:
    simple_res = re.finditer(r"<ref>([^<>]*?)\|( ?)doi( ?)=( ?)([^<>]*?)( ?)\|([^<>]*?)</ref>", article_text)
    definition_res = re.finditer(r"<ref name=([^<>]*?)( ?)>([^<>]*?)\|( ?)doi( ?)=( ?)([^<>]*?)( ?)\|([^<>]*?)</ref>", article_text)
    identifier_res = re.finditer(r"<ref name=([^<>]*?)( ?)/>", article_text)

    tuples = []

    for m in simple_res:
        tuples.append((str(m[5]).rstrip(), m.start()))

    identifiers = {}
    for m in definition_res:
        val = str(m[7]).rstrip()
        identifiers[str(m[1])] = val
        tuples.append((val, m.start()))

    for m in identifier_res:
        key = str(m[1])
        if key in identifiers:
            tuples.append((identifiers[key], m.start()))

    return tuples

def text_before(article_text: str, index: int) -> tuple[str, str]:
    par_index = article_text.rfind("\n", 0, index)
    paragraph = article_text[par_index+1:index]

    print(paragraph)
    paragraph = re.sub(r"<(.*?)>", '$@', paragraph)
    paragraph = re.sub(r"\{\{(.*?)}}", '$@', paragraph)
    print(paragraph)
    paragraph = re.sub(r"\[\[([^\[]*?)\|", '', paragraph)
    paragraph = re.sub(r"[\[\]]", '', paragraph)

    rint = len(paragraph) - 1
    while rint >= 0 and paragraph[rint] in '$@':
        rint -= 1
    ref_index = paragraph.rfind("$@", 0, rint)
    inc = 1 if ref_index == -1 else 2
    reference = paragraph[ref_index+inc:].lstrip()

    paragraph = re.sub(r"\$@", '', paragraph)
    reference = re.sub(r"\$@", '', reference)

    return paragraph, reference


def crossref_abstract(doi: str) -> str:
    metadata = requests.get("https://api.crossref.org/works/{}".format(doi))
    if metadata.text == "Resource not found.":
        return "> No Resource"
    metadata_dict = json.loads(metadata.text)["message"]
    if "abstract" not in metadata_dict:
        # print(json.dumps(metadata_dict, indent=2))
        #print("NON", doi)
        return "> No Abstract"
    else:
        abstract = metadata_dict["abstract"]
        plain = re.finditer(r"<(.*?:)?p(.*?)>((.|\n)*?)</(.*?:)?p>", abstract)
        full_abstract = ""
        for p in plain:
            full_abstract += str(p[3]).strip() + "\n"

        return full_abstract

def test_parse(article: str, doi: str) -> tuple[str, str]:
    text = dump_contents([article])
    dois = all_dois(text)
    idx = -1
    for d in dois:
        if d[0] == doi:
            idx = d[1]
    sentence, paragraph = text_before(text, idx)
    return sentence, paragraph


if __name__ == '__main__':

    # Test wiki parsing for specific doi
    # for x in test_parse("Quantum entanglement", "10.1038/nature15759"):
    #     print(x)

    # Generate file of list article plaintext
    # pages = ["List of common misconceptions about arts and culture",
    #                                   "List of common misconceptions about science, technology, and mathematics",
    #                                   "List of common misconceptions about history"]
    # articles_plaintext = dump_contents(pages)
    # with open("misconcepts_dump.txt", 'w', encoding="UTF-8") as file:
    #     file.write(articles_plaintext)

    # Generate file of titles of articles to parse for citations
    # with open("misconcepts_dump.txt", 'r', encoding="UTF-8") as misconcept_file:
    #     articles_plaintext = misconcept_file.read()
    #     alist = articles_from_bullets(articles_plaintext)
    # with open("articles_to_source.txt", 'w', encoding="UTF-8") as articles_file:
    #     for a in alist:
    #         articles_file.write(a+"\n")

    # Find the DOIs in each of those articles
    # with open("articles_to_source.txt", 'r', encoding="UTF-8") as articles_file, \
    #         open("doi_locs.txt", 'w', encoding="UTF-8") as dois_file:
    #     dois_file.write("[\n")
    #     first = True
    #     i = 0
    #     for line in articles_file:
    #         if first:
    #             first = False
    #         else:
    #             dois_file.write(",\n")
    #         article = line.rstrip()
    #         print(i, article)
    #         i += 1
    #         wikitext = dump_contents([article])
    #         dois = all_dois(wikitext)
    #         dois_to_dict = {d[1]: d[0] for d in dois}
    #         with_article = {article: dois_to_dict}
    #         to_json = json.dumps(with_article, indent=2)
    #         dois_file.write(to_json)
    #     dois_file.write("\n]\n")

    # Save the paragraph and sentences preceeding each citation
    # with open("doi_locs.txt", 'r', encoding="UTF-8") as locs, \
    #         open("wiki_paragraphs.txt", 'w', encoding="UTF-8") as pars:
    #     line = " "
    #     locs.readline()
    #     pars.write("[\n")
    #     i = 0
    #     while True:
    #         dois_text = locs.readline()
    #         if dois_text[0] == ']':
    #             break
    #         line = ' '
    #         while line[0] == ' ':
    #             line = locs.readline()
    #             dois_text += line
    #         dois_text = dois_text.rstrip()
    #         if dois_text[-1] == ',':
    #             dois_text = dois_text[:-1]
    #         dois_dict = json.loads(dois_text)
    #
    #         article_title = next(iter(dois_dict))
    #         print(i, article_title)
    #         i += 1
    #         full_text = dump_contents([article_title])
    #         first = True
    #         for pair in dois_dict[article_title].items():
    #             partxt, reftxt = text_before(full_text, int(pair[0]))
    #             elem = {
    #                 "doi": pair[1],
    #                 "wiki_article": article_title,
    #                 "wiki_sentence": reftxt,
    #                 "wiki_paragraph": partxt
    #             }
    #             if i > 1 or not first:
    #                 pars.write(",\n")
    #             pars.write(json.dumps(elem, indent=2))
    #             if first:
    #                 first = False
    #     pars.write("\n]\n")

    # Get abstracts for all DOI citations
    # start_at = 0
    # with open("wiki_paragraphs.txt", 'r', encoding="UTF-8") as wiki_pars, \
    #         open("final_dataset.txt", 'a', encoding="UTF-8") as final:
    #     line = " "
    #     wiki_pars.readline()
    #     if start_at == 0:
    #         final.write("[\n")
    #     i = 0
    #     count_err = 0
    #     while True:
    #         pars_text = wiki_pars.readline()
    #         if pars_text[0] == ']':
    #             break
    #         line = ' '
    #         while line[0] == ' ':
    #             line = wiki_pars.readline()
    #             pars_text += line
    #         pars_text = pars_text.rstrip()
    #         if pars_text[-1] == ',':
    #             pars_text = pars_text[:-1]
    #         if i < start_at:
    #             i += 1
    #             continue
    #         pars_dict = json.loads(pars_text)
    #         print(i, pars_dict["wiki_article"])
    #         i += 1
    #         new_dict = pars_dict.copy()
    #         abstract_txt = crossref_abstract(pars_dict["doi"])
    #         new_dict["abstract"] = abstract_txt
    #         if len(abstract_txt) == 0:
    #             print("!!!!!!!", pars_dict["doi"])
    #         if abstract_txt[0] == '>':
    #             count_err += 1
    #         if i > 1:
    #             final.write(",\n")
    #         final.write(json.dumps(new_dict, indent=2))
    #         print("abstract %", 1 - count_err/float(i-start_at))
    #
    #     final.write("\n]\n")

    # Merging the abstracts from final_dataset with the sentences from wiki_paragraphs
    with open("wiki_paragraphs.txt", 'r', encoding='UTF-8') as wiki_file:
        all_wiki_data = json.load(wiki_file)
    wiki_dict = {}
    for x in all_wiki_data:
        if x["doi"] in wiki_dict:
            wiki_dict[x["doi"]].append(x)
        else:
            wiki_dict[x["doi"]] = [x]

    addressed_dois = {k for k in wiki_dict.keys()}

    with open("rawtext_dataset_og.txt", 'r', encoding='UTF-8') as og_final, \
            open("rawtext_dataset.txt", 'w', encoding='UTF-8') as new_final:
        line = " "
        og_final.readline()
        new_final.write("[\n")
        i = 0
        first = True
        while True:
            print(i)
            og_text = og_final.readline()
            if og_text[0] == ']':
                break
            line = ' '
            while line[0] == ' ':
                line = og_final.readline()
                og_text += line
            og_text = og_text.rstrip()
            if og_text[-1] == ',':
                og_text = og_text[:-1]
            og_dict = json.loads(og_text)

            doi = og_dict["doi"]

            if doi not in addressed_dois:
                #print("doi {} not available in {}".format(doi, og_dict["wiki_article"]))
                print(f"passing on doi {doi}")
                continue

            addressed_dois.remove(doi)

            wiki_entries = wiki_dict[doi]

            for we in wiki_entries:
                if og_dict["abstract"][0] == ">":
                    continue

                if not first:
                    new_final.write(",\n")
                else:
                    first = False
                new_dict = we.copy()
                text = og_dict["abstract"]
                cleantext = re.sub(r'<.*?>', '', text)
                new_dict["abstract"] = cleantext

                new_final.write(json.dumps(new_dict, indent=2))

            i += 1

        new_final.write("\n]\n")

    pass
