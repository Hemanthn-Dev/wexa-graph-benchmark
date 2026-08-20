import os
import time
import statistics

from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

URI = os.environ["COGNODB_URI"]
USERNAME = os.environ["COGNODB_USERNAME"]
PASSWORD = os.environ["COGNODB_PASSWORD"]

ITERATIONS = 100

driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
)


def filtered_lookup(session):
    result = session.run(
        """
        MATCH (u:User)
        WHERE u.id = $user_id
        RETURN u.id AS id
        """,
        user_id="1"
    )

    return result.single()


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

    print("Starting indexed/filtered lookup benchmark...")
    print(f"Iterations: {ITERATIONS}")
    print("Indexed property: User.id")
    print()

    with driver.session() as session:

        for _ in range(10):
            filtered_lookup(session)

        print("Warm-up completed.")
        print("Running measured queries...")

        for _ in range(ITERATIONS):

            start = time.perf_counter()

            result = filtered_lookup(session)

            elapsed = (
                time.perf_counter() - start
            ) * 1000

            if result is None:
                raise RuntimeError(
                    "User 1 was not found"
                )

            latencies.append(elapsed)

    print()
    print("Indexed/filtered lookup results")
    print("-------------------------------")
    print(f"Queries: {len(latencies)}")
    print(f"Min: {min(latencies):.3f} ms")
    print(f"Average: {statistics.mean(latencies):.3f} ms")
    print(f"p50: {percentile(latencies, 50):.3f} ms")
    print(f"p95: {percentile(latencies, 95):.3f} ms")
    print(f"Max: {max(latencies):.3f} ms")
    print()
    print("Indexed/filtered lookup completed.")

finally:

    driver.close()