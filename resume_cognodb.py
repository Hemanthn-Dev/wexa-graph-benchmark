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

BATCH_SIZE = 10000
SKIP_RELATIONSHIPS = 2000

driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD),
    connection_timeout=30,
    max_connection_lifetime=300
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


def main():

    rows = []

    with DATASET.open("r", encoding="utf-8") as file:
        for index, line in enumerate(file):

            if index < SKIP_RELATIONSHIPS:
                continue

            parts = line.strip().split()

            if len(parts) != 2:
                continue

            rows.append({
                "source": parts[0],
                "target": parts[1]
            })

    total = len(rows)

    print(f"Remaining relationships: {total:,}")
    print(f"Batch size: {BATCH_SIZE:,}")
    print()

    start = time.perf_counter()

    with driver.session() as session:

        for i in range(0, total, BATCH_SIZE):

            batch = rows[i:i + BATCH_SIZE]

            session.execute_write(
                create_relationships,
                batch
            )

            completed = min(i + len(batch), total)

            elapsed = time.perf_counter() - start
            rate = completed / elapsed if elapsed else 0

            print(
                f"Relationships added: "
                f"{completed:,}/{total:,} | "
                f"Rate: {rate:,.2f}/sec"
            )

    elapsed = time.perf_counter() - start

    print()
    print("Relationship loading completed")
    print("------------------------------")
    print(f"Added: {total:,}")
    print(f"Time: {elapsed:.2f} seconds")
    print(f"Throughput: {total / elapsed:,.2f} relationships/sec")


if __name__ == "__main__":
    try:
        driver.verify_connectivity()
        main()
    finally:
        driver.close()