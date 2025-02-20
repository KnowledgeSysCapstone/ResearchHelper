import requests
import xml.etree.ElementTree as ET
import re

def dump_contents(articles: list[str]) -> str:
    reqs = [requests.get("https://en.wikipedia.org/wiki/Special:Export/{}".format(p)) for p in articles]
    xmls = [r.text for r in reqs]
    ns = {"d": "http://www.mediawiki.org/xml/export-0.11/"}
    texts = []
    for x in xmls:
        root = ET.fromstring(x)
        elem = root.find("d:page/d:revision/d:text", ns)
        texts.append(elem.text)

    fulltext = "\n\n".join(t for t in texts)
    return fulltext

def articles_from_bullets(fulltext: str) -> list[str]:
    articles_list = []
    lines = fulltext.split("\n")
    for line in lines:
        if len(line) > 3 and line[0:2] == "* ":
            res = re.findall(r"\[\[(.*?)\]\]", line)
            cleaned = [x.split("|")[0].split("#")[0].lower() for x in res]
            remove_dupes = set(cleaned)
            articles_list.extend(remove_dupes)
    return articles_list


if __name__ == '__main__':
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

    pass
