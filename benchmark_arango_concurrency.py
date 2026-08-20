import os
import time
import statistics
import warnings
import urllib3

warnings.filterwarnings(
    "ignore",
    category=urllib3.exceptions.InsecureRequestWarning
)

from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
from arango import ArangoClient

load_dotenv()

client = ArangoClient(
    hosts=os.environ["ARANGO_HOST"],
    verify_override=False
)

db = client.db(
    "_system",
    username=os.environ["ARANGO_USERNAME"],
    password=os.environ["ARANGO_PASSWORD"]
)

WORKERS = 10
REQUESTS = 100

USER_IDS = [
    "1", "13", "11", "6", "3",
    "4", "5", "15", "14", "7"
]


def read_user(user_id):
    start = time.perf_counter()

    cursor = db.aql.execute(
        """
        FOR u IN users
            FILTER u.id == @user_id
            RETURN u.id
        """,
        bind_vars={"user_id": user_id}
    )

    next(cursor, None)

    return "READ", (time.perf_counter() - start) * 1000


def write_user(user_id):
    start = time.perf_counter()

    db.aql.execute(
        """
        FOR u IN users
            FILTER u.id == @user_id
            UPDATE u WITH {
    benchmark_write: @value
} IN users
OPTIONS {
    ignoreErrors: true
}
        """,
        bind_vars={
            "user_id": user_id,
            "value": time.time()
        }
    )

    return "WRITE", (time.perf_counter() - start) * 1000


def percentile(values, p):
    values = sorted(values)
    index = (len(values) - 1) * p / 100
    lower = int(index)
    upper = min(lower + 1, len(values) - 1)

    if lower == upper:
        return values[lower]

    weight = index - lower

    return (
        values[lower]
        + (values[upper] - values[lower]) * weight
    )


print("Starting ArangoDB mixed read/write concurrency benchmark...")
print(f"Workers: {WORKERS}")
print(f"Requests: {REQUESTS}")
print("Read mix: 80%")
print("Write mix: 20%")
print()

tasks = []

for i in range(80):
    tasks.append(("READ", USER_IDS[i % len(USER_IDS)]))

WRITE_USER_IDS = [
    "101", "102", "103", "104", "105",
    "106", "107", "108", "109", "110",
    "111", "112", "113", "114", "115",
    "116", "117", "118", "119", "120"
]

for i in range(20):
    tasks.append(
        ("WRITE", WRITE_USER_IDS[i])
    )

print("Warm-up completed.")
print("Running concurrent workload...")

latencies = []
read_latencies = []
write_latencies = []

start_total = time.perf_counter()

with ThreadPoolExecutor(max_workers=WORKERS) as executor:

    futures = []

    for operation, user_id in tasks:

        if operation == "READ":
            futures.append(
                executor.submit(read_user, user_id)
            )
        else:
            futures.append(
                executor.submit(write_user, user_id)
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
print("ArangoDB Mixed Concurrency Results")
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
print(f"p50: {percentile(latencies, 50):.3f} ms")
print(f"p95: {percentile(latencies, 95):.3f} ms")

print()
print("Read latency")
print(f"p50: {percentile(read_latencies, 50):.3f} ms")
print(f"p95: {percentile(read_latencies, 95):.3f} ms")

print()
print("Write latency")
print(f"p50: {percentile(write_latencies, 50):.3f} ms")
print(f"p95: {percentile(write_latencies, 95):.3f} ms")

print()
print("ArangoDB mixed concurrency benchmark completed.")