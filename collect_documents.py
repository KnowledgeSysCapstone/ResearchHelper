import json
from typing import Iterator

import requests
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer
from spacy.lang.en import English
import lxml  # needed for BeautifulSoup XML parser

# Use SentenceBERT model
model = SentenceTransformer("all-MiniLM-L6-v2")

def get_journals(keyword: str, min_abstracts: int, do_print: bool) -> Iterator[str]:
    """Collects journals from CrossRef that match a query

    Parameters
    ----------
    keyword : str
        Word or phrase used to query CrossRef for journals.
    min_abstracts : int
        Minimum number of abstracts in journal. Journals with less are not returned.
    do_print : bool
        Whether to print progress through API calls.

    Yields
    ------
    str
        Next ISSN for electronic edition of journal matching query.
    """
    cursor = '*'  # Cursor for iterating pages
    # issns = []
    count = 0
    total_journals = -1
    i = 0

    # Iterate over pages
    while cursor:
        # Query metadata for next page
        resp = requests.get("https://api.crossref.org/journals?query={}&cursor={}".format(keyword, cursor))
        metadata = json.loads(resp.text)["message"]
        cursor = metadata["next-cursor"] if len(metadata["items"]) == metadata["items-per-page"] else ""

        if total_journals < 0:
            total_journals = metadata["total-results"]

        # Iterate journals on page
        for journal in metadata["items"]:
            i += 1
            # Calculate number of usable abstracts in the journal by multiply total DOIs by coverage
            contrib = journal["counts"]["total-dois"] * journal["coverage-type"]["all"]["abstracts"]
            if contrib > min_abstracts:
                # Add electronic ISSN for journal if it has enough abstracts
                for x in journal["issn-type"]:
                    if x["type"] == 'electronic':

                        if do_print:
                            print(f"Journal {i} out of {total_journals}")

                        yield x["value"]
                        break

                # issns.extend([x["value"] for x in journal["issn-type"] if x["type"] == 'electronic'])
                count += contrib

    # print("total journals", total_journals)
    # print("useful issns", len(issns))
    # print("dois", count)

    # return issns


def get_papers(issns: Iterator[str], min_cited: int, do_print: bool) -> Iterator[dict[str]]:
    """Collects the most highly cited papers from the given journal.

    Parameters
    ----------
    issns : Iterator of str
        Iterator for ISSNs representing journals to get papers from.
    min_cited : int
        Minimum number of times a paper must be cited by other papers in CrossRef in order to be included.
    do_print : bool
        Whether to print progress through API calls.

    Yields
    ------
    dict of str
        Metadata for next DOI.
    """
    for issn in issns:
        cursor = "*"  # Cursor for iterating pages
        total_papers = -1
        count_accept = 0
        # ret_obj = {}

        # Iterate over pages
        while cursor:

            # Query next page. Filters for journal articles with abstracts and sorts by number of times cited
            resp = requests.get("https://api.crossref.org/works/?filter=issn:{},type:journal-article,"
                                "has-abstract:true&sort=is-referenced-by-count&select=DOI,author,published,title,"
                                "container-title,volume,issue,page,indexed,abstract,is-referenced-by-count,type,"
                                "ISSN&cursor={}".format(issn, cursor))
            metadata = json.loads(resp.text)["message"]
            cursor = metadata["next-cursor"] if len(metadata["items"]) == metadata["items-per-page"] else ""

            if total_papers < 0:
                total_papers = metadata["total-results"]

            # Iterate over papers on page
            for paper in metadata["items"]:
                count_accept += 1
                if do_print:
                    print("\r", "                                                                         ", end='')
                    print("\r",
                          f"acc:{count_accept - 1} total:{total_papers} refs:{paper['is-referenced-by-count']}",
                          end='')
                if paper["is-referenced-by-count"] >= min_cited:
                    # Accept paper and add metadata paper to return object
                    yield paper

                    # ret_obj[paper["DOI"]] = paper

                else:
                    # Once citations drop below minimum, stop iterating this journal
                    cursor = ""
                    count_accept -= 1
                    break

        if do_print:
            print("\r", f"Journal {issn}. accept {count_accept} / {total_papers}")
        # return ret_obj


def parse_abstract(raw: str) -> str:
    """Converts XML string abstract as given by CrossRef into plaintext.

    Parameters
    ----------
    raw : str
        XML-formatted text containing abstract. Missing namespace declarations.

    Returns
    -------
    str
        Plaintext extracted from abstract.
    """
    # Parse using BeautifulSoup and lxml's XML parser
    soup = BeautifulSoup("<root>"+raw+"</root>", features="xml")
    # Find text with label 'p' or 'jats:p' and convert rest of tree to plaintext by removing all tags
    findp = soup.find('p')
    if findp:
        return findp.get_text()

    return soup.find('jats:p').get_text()


def separate_sentences(abstract: str) -> list[str]:
    """Split abstract text into list of sentences.

    Parameters
    ----------
    abstract : str
        Full text of abstract.

    Returns
    -------
    list of str
        List of individual sentences.
    """
    # Use the sentencizer from spaCy to maximize speed
    nlp = English()
    nlp.add_pipe("sentencizer")

    doc = nlp(abstract)
    return [sent.text.strip() for sent in doc.sents]


def embed_vectors(title: str, sentences: list[str]) -> dict[str, list[int]]:
    """Add titles to sentences for context and embed as vectors.

    Parameters
    ----------
    title : str
        Title of the paper. Used to add context to sentences.
    sentences: list of str
        List of sentences in the abstract.

    Returns
    -------
    dict of str
        Dictionary mapping title and sentence strings to their embedding vector.
    """
    # Input is title prepended to sentences
    input_text = [title + ": " + s for s in sentences]

    # Embed text into vectors
    embeddings = model.encode(input_text)
    return {inp: embed for inp, embed in zip(input_text, embeddings.tolist())}


def get_documents(keyword: str, min_abstracts: int = 1000, min_cited: int = 50,
                  do_print: bool = False) -> Iterator[dict[str]]:
    """Gets documents containing paper metadata and vectors from journals matching query.

    Parameters
    ----------
    keyword : str
        Word or phrase used to query CrossRef for journals.
    min_abstracts : int
        Minimum number of abstracts in journal. Journals with less are not returned.
    min_cited : int
        Minimum number of times a paper must be cited by other papers in CrossRef in order to be included.
    do_print : bool
        Whether to print progress through API calls.

    Yields
    ------
    dict of str
        Document of metadata and vectors for next paper.
    """

    journals_it = get_journals(keyword, min_abstracts, do_print)
    papers_it = get_papers(journals_it, min_cited, do_print)

    def reformat_date(og_dict, label):
        date_parts = ["year", "month", "day"]

        new_format = {}
        for i, p in enumerate(og_dict[label]["date-parts"][0]):
            new_format[date_parts[i]] = p
        og_dict[label] = new_format

    for paper in papers_it:
        abstract = paper["abstract"]
        parsed = parse_abstract(abstract)  # Convert abstract to plaintext
        if do_print:
            print(" - parsed", end='')
        sentenced = separate_sentences(parsed)  # Separate abstract into sentences
        if do_print:
            print(" - sentenced", end='')
        vectors = embed_vectors(paper["title"][0], sentenced)  # Embed sentences with title into vectors
        if do_print:
            print(" - embedded", end='')



        # Remove unnecessary info from certain fields
        paper["author"] = [{"given": x["given"], "family": x["family"]} for x in paper["author"]]
        paper["container-title"] = paper["container-title"][0]

        reformat_date(paper, "indexed")
        reformat_date(paper, "published")

        paper["text-type"] = paper["type"]
        del paper["type"]
        vectors_dicts = [{"vector": vectors[x], "title-and-sentence": x} for x in vectors]

        yield {
            "metadata": paper,
            "embedded_paper": vectors_dicts
        }


def elasticsearch_mappings() -> dict[str]:
    """Get mappings schema for Elasticsearch

    Returns
    -------
    dict of str
        Mappings dictionary describing the Elasticsearch schema that accepts this script's documents.

    """
    return {
        "mappings": {
            "properties": {
                "embedded_paper": {
                    "type": "nested",
                    "properties": {
                        "vector": {
                            "type": "dense_vector",
                            "dims": 384,
                            "index": True,
                            "similarity": "cosine"
                        },
                        "title-and-sentence": {
                            "type": "text"
                        }
                    }
                },
                "metadata": {
                    "type": "object",
                    "DOI": {"type": "keyword"},
                    "author": {
                        "type": "object",
                        "given": {"type": "text"},
                        "family": {"type": "text"}
                    },
                    "published": {
                        "type": "object",
                        "year": "integer",
                        "month": "integer",
                        "day": "integer"
                    },
                    "title": {"type": "text"},
                    "container-title": {"type": "text"},
                    "volume": {"type": "integer"},
                    "issue": {"type": "integer"},
                    "page": {"type": "text"},
                    "indexed": {
                        "type": "object",
                        "year": "integer",
                        "month": "integer",
                        "day": "integer"
                    },
                    "abstract": {"type": "text"},
                    "is-referenced-by-count": {"type": "integer"},
                    "text-type": {"type": "keyword"},
                    "ISSN": {"type": "keyword"}
                }
            }
        }
    }


def form_query(query: str, num_results: int) -> dict[str]:
    """Forms an Elasticsearch vector search query by embedding the given query string
    Parameters
    ----------
    query : str
        A user-submitted string to embed into a vector and search for similar sentences with
    num_results : int
        The number of closest documents to return

    Returns
    -------
    dict of str
        A query for Elasticsearch
    """

    embeddings = model.encode(query)

    return {
      "knn": {
        "field": "embedded_paper.vector",
        "query_vector": embeddings,
        "k": num_results,
        "num_candidates": 200,
        "inner_hits": {
          "_source": False,
          "fields": ["embedded_paper.title-and-sentence"],
          "size": 1
        }
      }
    }


if __name__ == '__main__':

    docs = get_documents("food", 5000, 1000, do_print=True)
    write_list = []
    for d in docs:
        write_list.append(d)

    with open("collected.json", 'w', encoding='UTF-8') as file:
        json.dump(write_list, file, indent=2)


#     ret_dict = {}
#     journals = get_journals("food", 5000)  # Get journals for a query
#     for j, journal in enumerate(journals):
#         papers = get_papers(journal, 1000)  # Get papers in the journal
#         for p, paper in enumerate(papers.values()):
#             abstract = paper["abstract"]
#             parsed = parse_abstract(abstract)  # Convert abstract to plaintext
#             sentenced = separate_sentences(parsed)  # Separate abstract into sentences
#             vectors = embed_vectors(paper["title"][0], sentenced)  # Embed sentences with title into vectors
#             doi = paper["DOI"]
#             ret_dict[doi] = {
#                 "metadata": paper,
#                 "embedding": vectors
#             }
#
#             print(f"{p+1}/{len(papers)}; {j+1}/{len(journals)}")
#
#     # Write to file to test
#     with open("collected.json", 'w', encoding='UTF-8') as collected:
#         json.dump(ret_dict, collected, indent=2)




