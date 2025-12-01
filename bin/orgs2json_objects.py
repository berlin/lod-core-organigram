import argparse
from rdflib import Graph, Namespace, Literal
from rdflib.namespace import ORG, RDFS, RDF
import logging
import json

BERORGS = Namespace("https://berlin.github.io/lod-vocabulary/berorgs/")

LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

parser = argparse.ArgumentParser(
    description="Create an array of JSON objects that can function as the data basis for an autocompletion endpoint.")
parser.add_argument('--input',
                    help="Path(s) to the input RDF file(s)",
                    type=str,
                    required=True,
                    nargs="+"
                    )
args = parser.parse_args()

graph = Graph()
for input in args.input:
    logging.info(f" reading graph at {input}")
    graph.parse(input)

orgs = []

query = """
PREFIX berorgs: <https://berlin.github.io/lod-vocabulary/berorgs/>
PREFIX lod_organigram: <https://berlin.github.io/lod-organigram/>
PREFIX lod_core_organigram: <https://berlin.github.io/lod-core-organigram/>
PREFIX org: <http://www.w3.org/ns/org#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?label ?org ?type ?abbreviation ?parent_label ?parent_abbreviation ?sort_key
WHERE {
    ?org 
        a ?type ;
        rdfs:label ?label ;
    .

    ?type rdfs:subClassOf* org:Organization .

    OPTIONAL {
        ?org org:unitOf/rdfs:label ?parent_label .
    }
    OPTIONAL {
        ?org org:unitOf/berorgs:abbreviation ?parent_abbreviation .
    }
    OPTIONAL {
        ?org berorgs:abbreviation ?abbreviation
    }

    # keep only the most specific type(s)
    FILTER NOT EXISTS {
        ?org a ?otherType .
        ?type rdfs:subClassOf+ ?otherType .
    }

    BIND(STR(CONCAT(COALESCE(?parent_label, ""), ?label)) AS ?raw_key)
    BIND(
        REPLACE(
            REPLACE(
                REPLACE(
                    REPLACE(
                        REPLACE(
                            REPLACE(
                                REPLACE(
                                    REPLACE(?raw_key,
                                    " I ",   " 1 "),
                                " II ",  " 2 "),
                            " III ", " 3 "),
                        " IV ",  " 4 "),
                    " V ",   " 5 "),
                " VI ",  " 6 "),
            " VII ", " 7 "),
        " VIII ", " 8 ") AS ?sort_key
    )    

}
ORDER BY ?sort_key
"""

result = graph.query(query)

orgs = []

for binding in result:
    org = {
        "id": binding['org'].split('/').pop(),
        "label": binding['label']
    }
    if binding['abbreviation']:
        org['abbreviation'] = binding['abbreviation']
    if binding['parent_label']:
        org['parent_label'] = binding['parent_label']
    if binding['parent_abbreviation']:
        org['parent_abbreviation'] = binding['parent_abbreviation']
    orgs.append(org)

print(json.dumps(orgs, indent=2))
