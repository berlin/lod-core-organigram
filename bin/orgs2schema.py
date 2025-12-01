import argparse
from rdflib import Graph, Namespace
from rdflib.namespace import ORG, RDFS, RDF
import logging
import json

BERORGS = Namespace("https://berlin.github.io/lod-vocabulary/berorgs/")

LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

OUTPUT_FORMATS = [ 'schema', 'select' ]
DEFAULT_FORMAT = 'schema'

parser = argparse.ArgumentParser(
    description="Create two JSON arrays of matching identifiers and labels to use as part of the Datenregister metadata schema")
parser.add_argument('--input',
                    help="Path to the input RDF file",
                    type=str,
                    required=True
                    )
parser.add_argument('--format',
                    help=f"Output format, one of [{'|'.join(OUTPUT_FORMATS)}]",
                    type=str,
                    default=DEFAULT_FORMAT
                    )
args = parser.parse_args()

graph = Graph()
logging.info(f" reading graph at {args.input}")
graph.parse(args.input)

author_uris = []

logging.info(" looking for organizations")
for org_res in graph.subjects(RDF.type, ORG.Organization):
    for label in graph.objects(org_res, RDFS.label):
        org_label = str(label)
        author_uris.append({ 'res': org_res, 'label': org_label})

logging.info(" sorting")
author_uris.sort(key=lambda organization: organization["label"])

extended_author_uris = []

for author_uri in author_uris:
    extended_author_uris.append({
        'id': author_uri['res'].split('/').pop(),
        'label': author_uri['label']
    })
    logging.info(f" looking for abbreviation of {author_uri['label']}")
    for abbrev_res in graph.objects(author_uri['res'], BERORGS.abbreviation):
        logging.info(f" found {abbrev_res}")
        abbreviation = str(abbrev_res)

    logging.info(f" looking for units of {author_uri['label']}")
    units = []
    for unit_res in graph.objects(author_uri['res'], ORG.hasUnit):
        logging.info(f" found {unit_res}")
        logging.info(f" looking for name of {unit_res}")
        for unit_label in graph.objects(unit_res, RDFS.label):
            logging.info(f" found '{unit_label}'")
            units.append({ 'res': unit_res, 'label': str(unit_label)})
    if len(units) > 0:
        units.sort(key=lambda unit: unit["label"])
        for unit in units:
            extended_author_uris.append({
                'id': unit['res'].split('/').pop(),
                'label': f"{abbreviation} – {unit['label']}"
            })

if args.format == 'schema':
    author_uri_schema = {
        "description": "Die URI der Organisation oder Organisationseinheit im Berliner Organigramm, die als veröffentlichende Stelle für diesen Datensatz gilt",
        "type": "string",
        "enum": [],
        "labels": [],
        "validator": "is_author_uri"
    }

    for entry in extended_author_uris:
        author_uri_schema['enum'].append(entry['id'])
        author_uri_schema['labels'].append(entry['label'])

    print(json.dumps(author_uri_schema, indent=2))
elif args.format == 'select':
    print(extended_author_uris)