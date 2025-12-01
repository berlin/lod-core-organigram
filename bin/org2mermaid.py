import argparse
from rdflib import Graph, URIRef
from rdflib.namespace import ORG, RDFS
import logging

LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


parser = argparse.ArgumentParser(
    description="Create a mermaid graph an org URI, displaying its (sub-)units and its super-organization.")
parser.add_argument('--input',
                    help="Path to the input RDF file",
                    type=str,
                    required=True
                    )
parser.add_argument('--uri',
                    help="URI of the org to build the graph for",
                    type=str,
                    required=True
                    )
args = parser.parse_args()

graph = Graph()
logging.info(f" reading graph at {args.input}")
graph.parse(args.input)

print("flowchart LR")
org_res = URIRef(args.uri)
org_name = "Organisation"

logging.info(f" looking for name of {org_res}")
for name in graph.objects(org_res, RDFS.label):
    org_name = str(name)
    logging.info(f" found '{org_name}'")
    print(f"    CORE(({org_name}))")
    
logging.info(f" looking for super-organizations of {org_res}")
for super_org in graph.objects(org_res, ORG.unitOf):
    logging.info(f" found {super_org}")
    for unit_name in graph.objects(super_org, RDFS.label):
        logging.info(f" found '{unit_name}'")
        print(f"    SUPER(({unit_name}))--> CORE")

logging.info(f" looking for units of {org_res}")
units = []
for unit in graph.objects(org_res, ORG.hasUnit):
    logging.info(f" found {unit}")
    logging.info(f" looking for name of {unit}")
    for unit_name in graph.objects(unit, RDFS.label):
        logging.info(f" found '{unit_name}'")
        units.append(unit_name)

units.sort() # bis 8 passt das auch bei römischer Nummerierung

for index, unit_name in enumerate(units):
    print(f"    CORE --> UNIT_{index}(({unit_name}))")

print("    style CORE fill:#111,stroke:#333,stroke-width:4px,color:#eee,font-weight: bold")
