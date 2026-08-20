import os
import time
import statistics

from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

URI = os.environ["COGNODB_URI"]
USERNAME = os.environ["COGNODB_USERNAME"]
PASSWORD = os.environ["COGNODB_PASSWORD"]

ITERATIONS = 30

driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
)


def aggregation(session):
    result = session.run(
        """
        MATCH ()-[r:CONNECTED_TO]->()
        RETURN count(r) AS total_relationships
        """
    )

    return result.single()["total_relationships"]


def percentile(values, percentile):
    values = sorted(values)

    index = (len(values) - 1) * percentile / 100

    lower = int(index)
    upper = min(lower + 1, len(values) - 1)

    if lower == upper:
        return values[lower]

    weight = index - lower

    return (
        values[lower]
        + (values[upper] - values[lower]) * weight
    )


try:

    driver.verify_connectivity()

    latencies = []

    with driver.session() as session:

        for _ in range(5):
            aggregation(session)

        print("Starting aggregation benchmark...")
        print(f"Iterations: {ITERATIONS}")
        print()

        for _ in range(ITERATIONS):

            start = time.perf_counter()

            total = aggregation(session)

            elapsed = (
                time.perf_counter() - start
            ) * 1000

            latencies.append(elapsed)

    print()
    print("Aggregation benchmark results")
    print("-----------------------------")
    print(f"Relationships counted: {total:,}")
    print(f"Queries: {len(latencies)}")
    print(f"Min: {min(latencies):.3f} ms")
    print(f"Average: {statistics.mean(latencies):.3f} ms")
    print(f"p50: {percentile(latencies, 50):.3f} ms")
    print(f"p95: {percentile(latencies, 95):.3f} ms")
    print(f"Max: {max(latencies):.3f} ms")
    print()
    print("✅ Aggregation benchmark completed.")

finally:

    driver.close()