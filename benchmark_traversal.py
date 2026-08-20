import os
import time
import statistics

from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

URI = os.environ["COGNODB_URI"]
USERNAME = os.environ["COGNODB_USERNAME"]
PASSWORD = os.environ["COGNODB_PASSWORD"]

USER_ID = "1"
ITERATIONS = 50

driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
)


def traversal(session):
    result = session.run(
        """
        MATCH (u:User {id: $user_id})-[:CONNECTED_TO]->(v:User)
        RETURN count(v) AS neighbors
        """,
        user_id=USER_ID
    )

    return result.single()["neighbors"]


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

        # Warm-up
        for _ in range(5):
            traversal(session)

        print("Starting traversal benchmark...")
        print(f"User: {USER_ID}")
        print(f"Iterations: {ITERATIONS}")
        print()

        for _ in range(ITERATIONS):

            start = time.perf_counter()

            neighbors = traversal(session)

            elapsed = (
                time.perf_counter() - start
            ) * 1000

            latencies.append(elapsed)

    print()
    print("Traversal benchmark results")
    print("---------------------------")
    print(f"Neighbors found: {neighbors}")
    print(f"Queries: {len(latencies)}")
    print(f"Min: {min(latencies):.3f} ms")
    print(f"Average: {statistics.mean(latencies):.3f} ms")
    print(f"p50: {percentile(latencies, 50):.3f} ms")
    print(f"p95: {percentile(latencies, 95):.3f} ms")
    print(f"Max: {max(latencies):.3f} ms")
    print()
    print("✅ Traversal benchmark completed.")

finally:

    driver.close()