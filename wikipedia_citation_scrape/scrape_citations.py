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

    # print([x.group(5) for x in simple_res])
    # print([(x.group(1), x.group(7)) for x in definition_res])
    # print([x.group(1) for x in identifier_res])

    return tuples


if __name__ == '__main__':
    #Generate file of list article plaintext
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
    with open("articles_to_source.txt", 'r', encoding="UTF-8") as articles_file, \
            open("doi_locs.txt", 'w', encoding="UTF-8") as dois_file:
        dois_file.write("[\n")
        first = True
        i = 0
        for line in articles_file:
            if first:
                first = False
            else:
                dois_file.write(",\n")
            article = line.rstrip()
            print(i, article)
            i += 1
            wikitext = dump_contents([article])
            dois = all_dois(wikitext)
            dois_to_dict = {d[1]: d[0] for d in dois}
            with_article = {article: dois_to_dict}
            to_json = json.dumps(with_article, indent=2)
            dois_file.write(to_json)
        dois_file.write("\n]\n")

    pass
