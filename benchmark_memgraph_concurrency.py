import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

URI = f"bolt+ssc://{os.environ['MEMGRAPH_HOST']}:{os.environ['MEMGRAPH_PORT']}"
USERNAME = os.environ["MEMGRAPH_USERNAME"]
PASSWORD = os.environ["MEMGRAPH_PASSWORD"]

WORKERS = 10
REQUESTS = 100

USER_IDS = [
    "1", "13", "11", "6", "3",
    "4", "5", "15", "14", "7"
]


def read_user(user_id):
    start = time.perf_counter()

    with driver.session() as session:
        result = session.run(
            """
            MATCH (u:User {id: $user_id})
            RETURN u.id AS id
            """,
            user_id=user_id
        )

        if result.single() is None:
            raise RuntimeError("User not found")

    return "READ", (time.perf_counter() - start) * 1000


def write_user(user_id):
    start = time.perf_counter()

    with driver.session() as session:
        session.run(
            """
            MATCH (u:User {id: $user_id})
            SET u.benchmark_write = $value
            """,
            user_id=user_id,
            value=time.time()
        ).consume()

    return "WRITE", (time.perf_counter() - start) * 1000


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


driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
)

try:
    driver.verify_connectivity()

    print("Starting Memgraph mixed read/write concurrency benchmark...")
    print(f"Workers: {WORKERS}")
    print(f"Requests: {REQUESTS}")
    print("Read mix: 80%")
    print("Write mix: 20%")
    print()

    tasks = []

    for i in range(80):
        tasks.append(
            ("READ", USER_IDS[i % len(USER_IDS)])
        )

    for i in range(20):
        tasks.append(
            ("WRITE", USER_IDS[i % len(USER_IDS)])
        )

    print("Warm-up completed.")
    print("Running concurrent workload...")

    latencies = []
    read_latencies = []
    write_latencies = []

    start_total = time.perf_counter()

    with ThreadPoolExecutor(
        max_workers=WORKERS
    ) as executor:

        futures = []

        for operation, user_id in tasks:

            if operation == "READ":
                futures.append(
                    executor.submit(
                        read_user,
                        user_id
                    )
                )
            else:
                futures.append(
                    executor.submit(
                        write_user,
                        user_id
                    )
                )

        for future in as_completed(futures):

            operation, latency = future.result()

            latencies.append(latency)

            if operation == "READ":
                read_latencies.append(latency)
            else:
                write_latencies.append(latency)

    total_time = time.perf_counter() - start_total

    print()
    print("Memgraph Mixed Concurrency Results")
    print("-----------------------------------")
    print(f"Workers: {WORKERS}")
    print(f"Requests: {len(latencies)}")
    print(f"Reads: {len(read_latencies)}")
    print(f"Writes: {len(write_latencies)}")
    print(f"Total time: {total_time:.3f} seconds")
    print(
        f"Throughput: "
        f"{len(latencies) / total_time:.2f} requests/sec"
    )

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
    print("Memgraph mixed concurrency benchmark completed.")

finally:
    driver.close()