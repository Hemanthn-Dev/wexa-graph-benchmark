import os
import time

from dotenv import load_dotenv
from arango import ArangoClient

load_dotenv()

HOST = os.environ["ARANGO_HOST"]
USERNAME = os.environ["ARANGO_USERNAME"]
PASSWORD = os.environ["ARANGO_PASSWORD"]

DATASET = "data/soc-pokec-200k.txt"
BATCH_SIZE = 5000

client = ArangoClient(
    hosts=HOST,
    verify_override=False
)

db = client.db(
    "_system",
    username=USERNAME,
    password=PASSWORD
)

GRAPH_NAME = "wexa_graph"
VERTEX_COLLECTION = "users"
EDGE_COLLECTION = "connections"

if db.has_graph(GRAPH_NAME):
    db.delete_graph(
        GRAPH_NAME,
        drop_collections=True
    )

graph = db.create_graph(GRAPH_NAME)

users = graph.create_vertex_collection(
    VERTEX_COLLECTION
)

connections = graph.create_edge_definition(
    edge_collection=EDGE_COLLECTION,
    from_vertex_collections=[VERTEX_COLLECTION],
    to_vertex_collections=[VERTEX_COLLECTION]
)

relationships = []
user_ids = set()

print("Reading dataset...")

with open(DATASET, "r", encoding="utf-8") as file:

    for line in file:

        parts = line.strip().split()

        if len(parts) != 2:
            continue

        source, target = parts

        user_ids.add(source)
        user_ids.add(target)

        relationships.append({
            "_from": f"{VERTEX_COLLECTION}/{source}",
            "_to": f"{VERTEX_COLLECTION}/{target}"
        })

print(f"Unique users: {len(user_ids):,}")
print(f"Relationships: {len(relationships):,}")
print()

print("Phase 1: Creating users...")

start = time.perf_counter()

users.insert_many(
    [
        {"_key": user_id, "id": user_id}
        for user_id in user_ids
    ],
    overwrite=False
)

user_time = time.perf_counter() - start

print(
    f"Users: {len(user_ids):,}"
)
print(
    f"User loading time: {user_time:.2f} seconds"
)
print()

print("Phase 2: Creating relationships...")

start = time.perf_counter()

for i in range(0, len(relationships), BATCH_SIZE):

    batch = relationships[
        i:i + BATCH_SIZE
    ]

    connections.insert_many(
        batch,
        overwrite=False
    )

    loaded = min(
        i + len(batch),
        len(relationships)
    )

    print(
        f"Relationships: "
        f"{loaded:,}/{len(relationships):,}"
    )

relationship_time = time.perf_counter() - start

print(
    f"Relationship loading time: "
    f"{relationship_time:.2f} seconds"
)

total_time = user_time + relationship_time

print()
print("ArangoDB Loading Benchmark")
print("--------------------------")
print(f"Users: {len(user_ids):,}")
print(f"Relationships: {len(relationships):,}")
print(f"User ingest time: {user_time:.2f}s")
print(
    f"Relationship ingest time: "
    f"{relationship_time:.2f}s"
)
print(f"Total load time: {total_time:.2f}s")

print(
    f"Node throughput: "
    f"{len(user_ids) / user_time:,.2f} nodes/sec"
)

print(
    f"Relationship throughput: "
    f"{len(relationships) / relationship_time:,.2f} relationships/sec"
)

print()
print("ArangoDB loading completed successfully.")