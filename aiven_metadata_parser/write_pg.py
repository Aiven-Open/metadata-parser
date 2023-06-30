"Writes results to PG"

import argparse
import json
from networkx.readwrite.gml import read_gml
import psycopg2

parser = argparse.ArgumentParser(description="Push data to PG Database.")
parser.add_argument("uri", metavar="N", help="pass the PG URI")
args = parser.parse_args()
print(args.uri)
connstr = args.uri

try:
    conn = psycopg2.connect(connstr, connect_timeout=2)
except psycopg2.Error as err:
    conn = None
    print(str(err))

cur = conn.cursor()
cur.execute(
    """
    select exists(
        select * from information_schema.tables where table_name=%s
        )
    """,
    ("metadata_parser_nodes",),
)
if cur.fetchone()[0]:
    cur.execute("TRUNCATE TABLE metadata_parser_nodes cascade;")
    conn.commit()
else:
    cur.execute(open("pg_store_tbl.sql", "r").read())

G = read_gml("graph_data.gml")

for node in G.nodes():
    json_rep = json.loads(
        G.nodes[node]
        .get("title")
        .replace("<br>", "")
        .replace("'", '"')
        .replace("True", "true")
        .replace("False", "false")
        .replace("None", "[]")[1:-1]
    )
    print(json_rep["id"])
    cur.execute(
        "insert into metadata_parser_nodes values(%s, %s);",
        (json_rep["id"], json.dumps(json_rep)),
    )
conn.commit()


for edge in G.edges():
    json_rep = json.loads(
        G.edges[edge]["title"]
        .replace("<br>", "")
        .replace("'", '"')
        .replace("True", "true")
        .replace("False", "false")
        .replace("None", "[]")[1:-1]
    )
    print(json.dumps(json_rep))
    cur.execute(
        "insert into metadata_parser_edges values(%s, %s, %s);",
        (
            json_rep["from"],
            json_rep["to"],
            json.dumps(json_rep),
        ),
    )
    cur.execute(
        "insert into metadata_parser_edges values(%s, %s, %s);",
        (
            json_rep["to"],
            json_rep["from"],
            json.dumps(json_rep),
        ),
    )

conn.commit()
