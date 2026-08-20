import os
import time
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed

from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

URI = os.environ["COGNODB_URI"]
USERNAME = os.environ["COGNODB_USERNAME"]
PASSWORD = os.environ["COGNODB_PASSWORD"]

WORKERS = 10
REQUESTS = 100

USER_IDS = [
    "1", "13", "11", "6", "3",
    "4", "5", "15", "14", "7"
]

driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
)


def lookup(user_id):

    start = time.perf_counter()

    with driver.session() as session:

        result = session.run(
            """
            MATCH (u:User {id: $user_id})
            RETURN u.id AS id
            """,
            user_id=user_id
        )

        record = result.single()

        if record is None:
            raise RuntimeError(
                f"User {user_id} not found"
            )

    elapsed = (
        time.perf_counter() - start
    ) * 1000

    return elapsed


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

    print("Starting concurrency benchmark...")
    print(f"Workers: {WORKERS}")
    print(f"Requests: {REQUESTS}")
    print()

    latencies = []

    start_total = time.perf_counter()

    with ThreadPoolExecutor(
        max_workers=WORKERS
    ) as executor:

        futures = [
            executor.submit(
                lookup,
                USER_IDS[i % len(USER_IDS)]
            )
            for i in range(REQUESTS)
        ]

        for future in as_completed(futures):

            latencies.append(
                future.result()
            )

    total_time = (
        time.perf_counter() - start_total
    )

    throughput = (
        len(latencies) / total_time
    )

    print()
    print("Concurrency benchmark results")
    print("-----------------------------")
    print(f"Workers: {WORKERS}")
    print(f"Requests: {len(latencies)}")
    print(f"Total time: {total_time:.3f} seconds")
    print(f"Throughput: {throughput:.2f} requests/sec")
    print(f"p50: {percentile(latencies, 50):.3f} ms")
    print(f"p95: {percentile(latencies, 95):.3f} ms")
    print()
    print("✅ Concurrency benchmark completed.")

finally:

    driver.close()