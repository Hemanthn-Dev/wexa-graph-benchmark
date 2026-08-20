import os
import time
from pathlib import Path

from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

URI = os.environ["NEO4J_URI"]
USERNAME = os.environ["NEO4J_USERNAME"]
PASSWORD = os.environ["NEO4J_PASSWORD"]

DATASET = Path("data/soc-pokec-200k.txt")
BATCH_SIZE = 10_000

driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
)


def create_users(tx, ids):
    tx.run(
        """
        UNWIND $ids AS id
        CREATE (:User {id: id})
        """,
        ids=ids
    ).consume()


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


def load_dataset():

    print("Reading dataset...")

    relationships = []
    users = set()

    with DATASET.open("r", encoding="utf-8") as file:

        for line in file:

            parts = line.strip().split()

            if len(parts) != 2:
                continue

            source, target = parts

            relationships.append({
                "source": source,
                "target": target
            })

            users.add(source)
            users.add(target)

    print(f"Unique users: {len(users):,}")
    print(f"Relationships: {len(relationships):,}")
    print()

    user_ids = list(users)

    # -------------------------
    # PHASE 1
    # -------------------------

    print("Phase 1: Creating users...")

    start = time.perf_counter()

    with driver.session() as session:

        for i in range(0, len(user_ids), BATCH_SIZE):

            batch = user_ids[i:i + BATCH_SIZE]

            session.execute_write(
                create_users,
                batch
            )

            loaded = min(
                i + len(batch),
                len(user_ids)
            )

            print(
                f"Users: {loaded:,}/{len(user_ids):,}"
            )

    user_time = time.perf_counter() - start

    print(
        f"User loading time: "
        f"{user_time:.2f} seconds"
    )

    print()

    # -------------------------
    # PHASE 2
    # -------------------------

    print("Phase 2: Creating relationships...")

    start = time.perf_counter()

    with driver.session() as session:

        for i in range(0, len(relationships), BATCH_SIZE):

            batch = relationships[i:i + BATCH_SIZE]

            session.execute_write(
                create_relationships,
                batch
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
    print("Neo4j Loading Benchmark")
    print("-----------------------")
    print(f"Users: {len(users):,}")
    print(f"Relationships: {len(relationships):,}")
    print(f"User ingest time: {user_time:.2f}s")
    print(
        f"Relationship ingest time: "
        f"{relationship_time:.2f}s"
    )
    print(f"Total load time: {total_time:.2f}s")

    if user_time > 0:
        print(
            f"Node throughput: "
            f"{len(users) / user_time:,.2f} nodes/sec"
        )

    if relationship_time > 0:
        print(
            f"Relationship throughput: "
            f"{len(relationships) / relationship_time:,.2f} relationships/sec"
        )


if __name__ == "__main__":

    try:

        driver.verify_connectivity()

        load_dataset()

        print()
        print("Neo4j loading completed successfully.")

    finally:

        driver.close()