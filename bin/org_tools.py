import argparse
from encodings.punycode import T
import json
from uuid import UUID, uuid5

from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import ORG, RDF, RDFS

UUID_NAMESPACE_BERLIN_ORG = UUID('4254cc42-9a21-4846-be2b-afa909c6360a')
BERLIN_CORE_ORG = Namespace('https://berlin.github.io/lod-core-organigram/')
BERORGS = Namespace("https://berlin.github.io/lod-vocabulary/berorgs/")

def generate_uuid(components: list[str], namespace: UUID = UUID_NAMESPACE_BERLIN_ORG, separator: str = '|') -> str:
    """Generate a UUID based on the concatenation of strings in `components`.

    Args:
        components (list[str]): A list of strings to build the GUID from. For example the hierarchy of 
            organizations to generate the GUID for a sub-organizations.
            - [ "Senatsverwaltung für Arbeit, Soziales, Gleichstellung, Integration, Vielfalt und Antidiskriminierung" ]
            - [ "Senatsverwaltung für Arbeit, Soziales, Gleichstellung, Integration, Vielfalt und Antidiskriminierung", "Abteilung V – Frauen und Gleichstellung" ]
        namespace (UUID, optional): The namespace to be used in generating the UUID. Defaults to NAMESPACE_BERLIN_ORG.
        separator (str, optional): The separator to be used for concatenating the elements of `components`. Defaults to '|'.

    Returns:
        str: _description_
    """
    concat = separator.join(map(str, components))
    return uuid5(namespace, concat)

def generate_uriref(components: list[str], namespace: Namespace = BERLIN_CORE_ORG) -> URIRef:
    """Generate a rdflib `URIRef` from the list of strings in `components`.

    Args:
        components (list[str]): A list of strings to build the GUID from. For example the hierarchy of 
            organizations to generate the GUID for a sub-organizations.
            - [ "Senatsverwaltung für Arbeit, Soziales, Gleichstellung, Integration, Vielfalt und Antidiskriminierung" ]
            - [ "Senatsverwaltung für Arbeit, Soziales, Gleichstellung, Integration, Vielfalt und Antidiskriminierung", "Abteilung V – Frauen und Gleichstellung" ]
        namespace (Namespace, optional): The URI namespace to be used in the URIRef. Defaults to BERLIN_CORE_ORG.

    Returns:
        URIRef: the generated URIRef
    """
    uuid = generate_uuid(components)
    return namespace[f"org_{uuid}"]

parser = argparse.ArgumentParser(
    description="Convert a JSON source of organization names to RDF.")
parser.add_argument('--input',
                    help="Path to the input JSON file",
                    type=str,
                    required=True
                    )
parser.add_argument('--abbrev',
                    help="Path to the JSON file with org abbreviations",
                    type=str,
                    required=True
                    )
args = parser.parse_args()

graph = Graph()
graph.bind('core_org', BERLIN_CORE_ORG)
graph.bind('berorgs', BERORGS)

abbrev_file = open(args.abbrev)
abbreviations = json.load(abbrev_file)
abbrev_file.close()

with open(args.input) as org_names:
    data = json.load(org_names)
    
    for name_path in data['names']:
        org_res = generate_uriref(name_path)
        org_type = ORG.Organization
        if len(name_path) > 1:
            org_type = ORG.OrganizationalUnit
        graph.add( (org_res, RDF.type, org_type) )

        org_name = name_path[-1]

        graph.add( (org_res, RDFS.label, Literal(org_name, lang='de')))
        if org_name in abbreviations:
            graph.add( (org_res, BERORGS.abbreviation, Literal(abbreviations[org_name], lang='de')))

        name_path.pop()
        if len(name_path) > 0:
            parent_res = generate_uriref(name_path)
            graph.add( (org_res, ORG.unitOf, parent_res) )
            graph.add( (parent_res, ORG.hasUnit, org_res) )

print(graph.serialize())