import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

URI = os.environ["NEO4J_URI"]
USERNAME = os.environ["NEO4J_USERNAME"]
PASSWORD = os.environ["NEO4J_PASSWORD"]

WORKERS = 10
REQUESTS = 100

READ_PERCENT = 80
WRITE_PERCENT = 20

USER_IDS = [
    "1", "13", "11", "6", "3",
    "4", "5", "15", "14", "7"
]

driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
)


def read_user(user_id):

    start = time.perf_counter()

    with driver.session() as session:

        record = session.run(
            """
            MATCH (u:User {id: $user_id})
            RETURN u.id AS id
            """,
            user_id=user_id
        ).single()

        if record is None:
            raise RuntimeError(
                f"User {user_id} not found"
            )

    return "READ", (
        time.perf_counter() - start
    ) * 1000


def write_user(user_id):

    start = time.perf_counter()

    with driver.session() as session:

        session.run(
            """
            MATCH (u:User {id: $user_id})
            SET u.benchmark_write = $value
            RETURN u.id
            """,
            user_id=user_id,
            value=time.time()
        ).consume()

    return "WRITE", (
        time.perf_counter() - start
    ) * 1000


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

    print("Starting Neo4j mixed read/write concurrency benchmark...")
    print(f"Workers: {WORKERS}")
    print(f"Requests: {REQUESTS}")
    print(f"Read mix: {READ_PERCENT}%")
    print(f"Write mix: {WRITE_PERCENT}%")
    print()

    with driver.session() as session:

        for user_id in USER_IDS:

            session.run(
                """
                MATCH (u:User {id: $user_id})
                RETURN u.id
                """,
                user_id=user_id
            ).consume()

    print("Warm-up completed.")
    print("Running concurrent workload...")

    read_requests = int(
        REQUESTS * READ_PERCENT / 100
    )

    write_requests = (
        REQUESTS - read_requests
    )

    tasks = []

    for i in range(read_requests):
        tasks.append(
            ("READ", USER_IDS[i % len(USER_IDS)])
        )

    for i in range(write_requests):
        tasks.append(
            ("WRITE", USER_IDS[i % len(USER_IDS)])
        )

    latencies = []
    read_latencies = []
    write_latencies = []

    start_total = time.perf_counter()

    with ThreadPoolExecutor(
        max_workers=WORKERS
    ) as executor:

        future_map = {}

        for operation, user_id in tasks:

            if operation == "READ":
                future = executor.submit(
                    read_user,
                    user_id
                )
            else:
                future = executor.submit(
                    write_user,
                    user_id
                )

            future_map[future] = operation

        for future in as_completed(future_map):

            operation, latency = future.result()

            latencies.append(latency)

            if operation == "READ":
                read_latencies.append(latency)
            else:
                write_latencies.append(latency)

    total_time = (
        time.perf_counter()
        - start_total
    )

    throughput = len(latencies) / total_time

    print()
    print("Neo4j Mixed Concurrency Results")
    print("--------------------------------")
    print(f"Workers: {WORKERS}")
    print(f"Requests: {len(latencies)}")
    print(f"Reads: {len(read_latencies)}")
    print(f"Writes: {len(write_latencies)}")
    print(f"Total time: {total_time:.3f} seconds")
    print(f"Throughput: {throughput:.2f} requests/sec")

    print()
    print("Overall latency")
    print(
        f"p50: {percentile(latencies, 50):.3f} ms"
    )
    print(
        f"p95: {percentile(latencies, 95):.3f} ms"
    )

    print()
    print("Read latency")
    print(
        f"p50: {percentile(read_latencies, 50):.3f} ms"
    )
    print(
        f"p95: {percentile(read_latencies, 95):.3f} ms"
    )

    print()
    print("Write latency")
    print(
        f"p50: {percentile(write_latencies, 50):.3f} ms"
    )
    print(
        f"p95: {percentile(write_latencies, 95):.3f} ms"
    )

    print()
    print("Neo4j mixed concurrency benchmark completed.")

finally:

    driver.close()