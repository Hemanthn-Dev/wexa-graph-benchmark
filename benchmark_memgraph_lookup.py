import os
import time
import statistics

from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

URI = f"bolt+ssc://{os.environ['MEMGRAPH_HOST']}:{os.environ['MEMGRAPH_PORT']}"
USERNAME = os.environ["MEMGRAPH_USERNAME"]
PASSWORD = os.environ["MEMGRAPH_PASSWORD"]

USER_IDS = ["1", "13", "11", "6", "3", "4", "5", "15", "14", "7"]
ITERATIONS = 100

driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
)


def lookup(session, user_id):
    return session.run(
        """
        MATCH (u:User {id: $user_id})
        RETURN u.id AS id
        """,
        user_id=user_id
    ).single()


def percentile(values, p):
    values = sorted(values)
    index = (len(values) - 1) * p / 100
    lower = int(index)
    upper = min(lower + 1, len(values) - 1)

    if lower == upper:
        return values[lower]

    weight = index - lower
    return values[lower] + (values[upper] - values[lower]) * weight


try:
    driver.verify_connectivity()

    latencies = []

    print("Starting Memgraph indexed lookup benchmark...")
    print(f"Iterations: {ITERATIONS}")
    print("Indexed property: User.id")
    print()

    with driver.session() as session:

        for user_id in USER_IDS:
            lookup(session, user_id)

        print("Warm-up completed.")
        print("Running measured queries...")

        for i in range(ITERATIONS):

            user_id = USER_IDS[i % len(USER_IDS)]

            start = time.perf_counter()

            result = lookup(session, user_id)

            elapsed = (time.perf_counter() - start) * 1000

            if result is None:
                raise RuntimeError(
                    f"User {user_id} was not found"
                )

            latencies.append(elapsed)

    print()
    print("Memgraph Indexed Lookup Results")
    print("--------------------------------")
    print(f"Queries: {len(latencies)}")
    print(f"Min: {min(latencies):.3f} ms")
    print(f"Average: {statistics.mean(latencies):.3f} ms")
    print(f"p50: {percentile(latencies, 50):.3f} ms")
    print(f"p95: {percentile(latencies, 95):.3f} ms")
    print(f"Max: {max(latencies):.3f} ms")
    print()
    print("Memgraph indexed lookup completed.")

finally:
    driver.close()