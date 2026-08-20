import os
import time

from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

URI = (
    "bolt+ssc://"
    + os.environ["MEMGRAPH_HOST"]
    + ":"
    + os.environ["MEMGRAPH_PORT"]
)

USERNAME = os.environ["MEMGRAPH_USERNAME"]
PASSWORD = os.environ["MEMGRAPH_PASSWORD"]

DATASET = "data/soc-pokec-200k.txt"
BATCH_SIZE = 1000

driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
)


def create_relationships(tx, rows):
    tx.run(
        """
        UNWIND $rows AS row
        MATCH (source:User {id: row.source})
        MATCH (target:User {id: row.target})
        CREATE (source)-[:CONNECTED_TO]->(target)
        """,
        rows=rows
    ).consume()


try:

    driver.verify_connectivity()

    print("Reading relationships...")

    rows = []

    with open(DATASET, "r", encoding="utf-8") as file:

        for line in file:

            parts = line.strip().split()

            if len(parts) != 2:
                continue

            rows.append({
                "source": parts[0],
                "target": parts[1]
            })

    print(f"Relationships: {len(rows):,}")
    print(f"Batch size: {BATCH_SIZE}")
    print()

    start = time.perf_counter()

    with driver.session() as session:

        for i in range(0, len(rows), BATCH_SIZE):

            batch = rows[i:i + BATCH_SIZE]

            session.execute_write(
                create_relationships,
                batch
            )

            loaded = min(
                i + len(batch),
                len(rows)
            )

            print(
                f"Relationships: "
                f"{loaded:,}/{len(rows):,}"
            )

    elapsed = time.perf_counter() - start

    print()
    print("Memgraph Relationship Loading")
    print("-----------------------------")
    print(f"Relationships: {len(rows):,}")
    print(f"Time: {elapsed:.2f} seconds")
    print(
        f"Throughput: "
        f"{len(rows) / elapsed:,.2f} relationships/sec"
    )

finally:

    driver.close()