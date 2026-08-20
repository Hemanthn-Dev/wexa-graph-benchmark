import os
import time
import statistics

from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

URI = os.environ["NEO4J_URI"]
USERNAME = os.environ["NEO4J_USERNAME"]
PASSWORD = os.environ["NEO4J_PASSWORD"]

USER_IDS = [
    "1", "13", "11", "6", "3",
    "4", "5", "15", "14", "7"
]

ITERATIONS = 100

driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
)


def lookup_user(session, user_id):

    result = session.run(
        """
        MATCH (u:User {id: $user_id})
        RETURN u.id AS id
        """,
        user_id=user_id
    )

    return result.single()


def percentile(values, percentile):

    values = sorted(values)

    index = (len(values) - 1) * percentile / 100

    lower = int(index)
    upper = min(
        lower + 1,
        len(values) - 1
    )

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

    print("Starting Neo4j lookup benchmark...")
    print(f"Iterations: {ITERATIONS}")
    print()

    with driver.session() as session:

        for user_id in USER_IDS:
            lookup_user(session, user_id)

        print("Warm-up completed.")
        print("Running measured queries...")

        for i in range(ITERATIONS):

            user_id = USER_IDS[
                i % len(USER_IDS)
            ]

            start = time.perf_counter()

            result = lookup_user(
                session,
                user_id
            )

            elapsed = (
                time.perf_counter()
                - start
            ) * 1000

            if result is None:
                raise RuntimeError(
                    f"User {user_id} not found"
                )

            latencies.append(elapsed)

    print()
    print("Neo4j Lookup Benchmark Results")
    print("------------------------------")
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
    print("Neo4j lookup benchmark completed.")

finally:

    driver.close()