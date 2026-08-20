import os
import time
from pathlib import Path

from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

URI = os.environ["COGNODB_URI"]
USERNAME = os.environ["COGNODB_USERNAME"]
PASSWORD = os.environ["COGNODB_PASSWORD"]

DATASET = Path("data/soc-pokec-200k.txt")
BATCH_SIZE = 2000

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

    # -------------------------
    # PHASE 1: CREATE USERS
    # -------------------------

    print("Phase 1: Creating users...")

    user_ids = list(users)

    start_users = time.perf_counter()

    with driver.session() as session:

        for i in range(0, len(user_ids), BATCH_SIZE):

            batch = user_ids[i:i + BATCH_SIZE]

            session.execute_write(
                create_users,
                batch
            )

            print(
                f"Users: "
                f"{min(i + len(batch), len(user_ids)):,}/"
                f"{len(user_ids):,}"
            )

    user_time = time.perf_counter() - start_users

    print(f"User loading time: {user_time:.2f} seconds")
    print()

    # -------------------------
    # PHASE 2: RELATIONSHIPS
    # -------------------------

    print("Phase 2: Creating relationships...")

    start_relationships = time.perf_counter()

    with driver.session() as session:

        for i in range(0, len(relationships), BATCH_SIZE):

            batch = relationships[i:i + BATCH_SIZE]

            session.execute_write(
                create_relationships,
                batch
            )

            print(
                f"Relationships: "
                f"{min(i + len(batch), len(relationships)):,}/"
                f"{len(relationships):,}"
            )

    relationship_time = time.perf_counter() - start_relationships

    print(f"Relationship loading time: {relationship_time:.2f} seconds")
    print()

    total_time = user_time + relationship_time

    print("Loading benchmark")
    print("-----------------")
    print(f"Users: {len(users):,}")
    print(f"Relationships: {len(relationships):,}")
    print(f"User ingest time: {user_time:.2f}s")
    print(f"Relationship ingest time: {relationship_time:.2f}s")
    print(f"Total load time: {total_time:.2f}s")

    print()

    print(
        f"Node throughput: "
        f"{len(users) / user_time:,.2f} nodes/sec"
    )

    print(
        f"Relationship throughput: "
        f"{len(relationships) / relationship_time:,.2f} relationships/sec"
    )


if __name__ == "__main__":

    try:
        driver.verify_connectivity()
        load_dataset()

        print()
        print("✅ Loading completed.")

    finally:
        driver.close()