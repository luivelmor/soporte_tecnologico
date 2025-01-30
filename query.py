from owlready2 import *

def get_authors_with_cited_references(onto):
    """
    Returns a list of authors who have at least one cited reference.
    """
    sync_reasoner()

    influential_authors = set()
    for ref in onto.ReferenciaBibliografica.instances():
        if ref.citaA:  # If the reference has been cited
            for author in ref.escritoPor:
                influential_authors.add(author)

    print(f"Found {len(influential_authors)} authors with cited references.")
    return list(influential_authors)


def get_references_with_multiple_authors(onto):
    """
    Returns a list of references that have two or more authors.
    """
    sync_reasoner()

    references = [ref for ref in onto.ReferenciaBibliografica.instances() if len(ref.escritoPor) >= 2]

    print(f"Found {len(references)} references with multiple authors.")
    return references


# Usage:
onto = get_ontology("bibliographic_ontology_updated.owl").load()

# 1. ¿Qué autores tienen al menos una referencia que ha sido citada?
print(get_authors_with_cited_references(onto))

# 2. ¿Qué referencias bibliográficas tienen dos o más autores?
print(get_references_with_multiple_authors(onto))