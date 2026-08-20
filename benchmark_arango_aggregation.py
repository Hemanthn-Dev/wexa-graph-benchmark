import os
import time
import statistics
import warnings
import urllib3

warnings.filterwarnings(
    "ignore",
    category=urllib3.exceptions.InsecureRequestWarning
)

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

ITERATIONS = 30


def aggregation():
    cursor = db.aql.execute(
        """
        RETURN LENGTH(
            FOR e IN connections
                RETURN 1
        )
        """
    )

    return next(cursor)


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


print("Starting ArangoDB aggregation benchmark...")
print(f"Iterations: {ITERATIONS}")
print()

for _ in range(5):
    aggregation()

print("Warm-up completed.")
print("Running measured queries...")

latencies = []

for _ in range(ITERATIONS):

    start = time.perf_counter()

    total = aggregation()

    elapsed = (
        time.perf_counter() - start
    ) * 1000

    latencies.append(elapsed)

print()
print("ArangoDB Aggregation Benchmark Results")
print("---------------------------------------")
print(f"Relationships counted: {total:,}")
print(f"Queries: {len(latencies)}")
print(f"Min: {min(latencies):.3f} ms")
print(f"Average: {statistics.mean(latencies):.3f} ms")
print(f"p50: {percentile(latencies, 50):.3f} ms")
print(f"p95: {percentile(latencies, 95):.3f} ms")
print(f"Max: {max(latencies):.3f} ms")
print()
print("ArangoDB aggregation benchmark completed.")