import os
import time
import statistics

from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

URI = f"bolt+ssc://{os.environ['MEMGRAPH_HOST']}:{os.environ['MEMGRAPH_PORT']}"
USERNAME = os.environ["MEMGRAPH_USERNAME"]
PASSWORD = os.environ["MEMGRAPH_PASSWORD"]

ITERATIONS = 100

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


def percentile(values, p):

    values = sorted(values)

    index = (len(values) - 1) * p / 100

    lower = int(index)
    upper = min(lower + 1, len(values) - 1)

    if lower == upper:
        return values[lower]

    weight = index - lower

    return values[lower] + (
        values[upper] - values[lower]
    ) * weight


try:

    driver.verify_connectivity()

    latencies = []

    print("Starting Memgraph aggregation benchmark...")
    print(f"Iterations: {ITERATIONS}")
    print()

    with driver.session() as session:

        for _ in range(10):
            aggregation(session)

        print("Warm-up completed.")
        print("Running measured queries...")

        for _ in range(ITERATIONS):

            start = time.perf_counter()

            total = aggregation(session)

            elapsed = (
                time.perf_counter() - start
            ) * 1000

            latencies.append(elapsed)

    print()
    print("Memgraph Aggregation Benchmark Results")
    print("---------------------------------------")
    print(f"Relationships counted: {total:,}")
    print(f"Queries: {len(latencies)}")
    print(f"Min: {min(latencies):.3f} ms")
    print(
        f"Average: "
        f"{statistics.mean(latencies):.3f} ms"
    )
    print(
        f"p50: "
        f"{percentile(latencies, 50):.3f} ms"
    )
    print(
        f"p95: "
        f"{percentile(latencies, 95):.3f} ms"
    )
    print(f"Max: {max(latencies):.3f} ms")
    print()
    print("Memgraph aggregation benchmark completed.")

finally:

    driver.close()