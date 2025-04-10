import json
from typing import Iterator

import requests
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer
from spacy.lang.en import English
import lxml  # needed for BeautifulSoup XML parser


def get_journals(keyword: str, min_abstracts: int) -> Iterator[str]:
    """Collects journals from CrossRef that match a query

    Parameters
    ----------
    keyword : str
        Word or phrase used to query CrossRef for journals.
    min_abstracts : int
        Minimum number of abstracts in journal. Journals with less are not returned.

    Yields
    ------
    str
        Next ISSN for electronic edition of journal matching query.
    """
    cursor = '*'  # Cursor for iterating pages
    # issns = []
    # count = 0
    # total_journals = -1
    # i = 0

    # Iterate over pages
    while cursor:
        # print(i)
        # i += 1

        # Query metadata for next page
        resp = requests.get("https://api.crossref.org/journals?query={}&cursor={}".format(keyword, cursor))
        metadata = json.loads(resp.text)["message"]
        cursor = metadata["next-cursor"] if len(metadata["items"]) == metadata["items-per-page"] else ""

        # if total_journals < 0:
        #     total_journals = metadata["total-results"]

        # Iterate journals on page
        for journal in metadata["items"]:
            # Calculate number of usable abstracts in the journal by multiply total DOIs by coverage
            contrib = journal["counts"]["total-dois"] * journal["coverage-type"]["all"]["abstracts"]
            if contrib > min_abstracts:
                # Add electronic ISSN for journal if it has enough abstracts
                for x in journal["issn-type"]:
                    if x["type"] == 'electronic':
                        yield x["value"]
                        break

                # issns.extend([x["value"] for x in journal["issn-type"] if x["type"] == 'electronic'])
                # count += contrib

    # print("total journals", total_journals)
    # print("useful issns", len(issns))
    # print("dois", count)

    # return issns


def get_papers(issns: Iterator[str], min_cited: int) -> Iterator[dict[str]]:
    """Collects the most highly cited papers from the given journal.

    Parameters
    ----------
    issns : Iterator of str
        Iterator for ISSNs representing journals to get papers from.
    min_cited : int
        Minimum number of times a paper must be cited by other papers in CrossRef in order to be included.

    Yields
    ------
    dict of str
        Metadata for next DOI.
    """
    for issn in issns:
        cursor = "*"  # Cursor for iterating pages
        # total_papers = -1
        # count_accept = 0
        # ret_obj = {}

        # Iterate over pages
        while cursor:
            # Query next page. Filters for journal articles with abstracts and sorts by number of times cited
            resp = requests.get("https://api.crossref.org/works/?filter=issn:{},type:journal-article,"
                                "has-abstract:true&sort=is-referenced-by-count&select=DOI,abstract,article-number,"
                                "author,container-title,group-title,is-referenced-by-count,issn-type,issue,link,page,"
                                "published,publisher,publisher-location,short-title,subject,subtitle,title,translator,"
                                "type,volume&cursor={}".format(issn, cursor))
            metadata = json.loads(resp.text)["message"]
            cursor = metadata["next-cursor"] if len(metadata["items"]) == metadata["items-per-page"] else ""

            # if total_papers < 0:
            #     total_papers = metadata["total-results"]

            # Iterate over papers on page
            for paper in metadata["items"]:
                if paper["is-referenced-by-count"] >= min_cited:
                    # Accept paper and add metadata paper to return object
                    yield paper

                    # ret_obj[paper["DOI"]] = paper
                    # count_accept += 1
                else:
                    # Once citations drop below minimum, stop iterating this journal
                    cursor = ""
                    break

                # print("\r", f"acc:{count_accept} total:{total_papers} refs:{paper['is-referenced-by-count']}", end='')


        # print("\r", f"Journal {issn}. accept {count_accept} / {total_papers}")
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
    # Use SentenceBERT model
    model = SentenceTransformer("all-MiniLM-L6-v2")

    # Input is title prepended to sentences
    input_text = [title + ": " + s for s in sentences]

    # Embed text into vectors
    embeddings = model.encode(input_text)
    return {inp: embed for inp, embed in zip(input_text, embeddings.tolist())}


def get_documents(keyword: str, min_abstracts: int = 1000, min_cited: int = 50) -> Iterator[dict[str]]:
    """Gets documents containing paper metadata and vectors from journals matching query.

    Parameters
    ----------
    keyword : str
        Word or phrase used to query CrossRef for journals.
    min_abstracts : int
        Minimum number of abstracts in journal. Journals with less are not returned.
    min_cited : int
        Minimum number of times a paper must be cited by other papers in CrossRef in order to be included.

    Yields
    ------
    dict of str
        Document of metadata and vectors for next paper.
    """

    journals_it = get_journals(keyword, min_abstracts)
    papers_it = get_papers(journals_it, min_cited)

    for paper in papers_it:
        abstract = paper["abstract"]
        parsed = parse_abstract(abstract)  # Convert abstract to plaintext
        sentenced = separate_sentences(parsed)  # Separate abstract into sentences
        vectors = embed_vectors(paper["title"][0], sentenced)  # Embed sentences with title into vectors
        yield {
            "metadata": paper,
            "embedding": vectors
        }


if __name__ == '__main__':

    docs = get_documents("food", 5000, 1000)
    for d in docs:
        print(d)


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




