import warnings
import urllib3

warnings.filterwarnings("ignore", category=urllib3.exceptions.InsecureRequestWarning)

import os
import time
import statistics

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

ITERATIONS = 100

USER_IDS = [
    "1", "13", "11", "6", "3",
    "4", "5", "15", "14", "7"
]


def lookup(user_id):
    cursor = db.aql.execute(
        """
        FOR u IN users
            FILTER u.id == @user_id
            RETURN u.id
        """,
        bind_vars={"user_id": user_id}
    )

    return next(cursor, None)


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


print("Starting ArangoDB lookup benchmark...")
print(f"Iterations: {ITERATIONS}")
print()

latencies = []

for user_id in USER_IDS:
    lookup(user_id)

print("Warm-up completed.")
print("Running measured queries...")

for i in range(ITERATIONS):

    user_id = USER_IDS[i % len(USER_IDS)]

    start = time.perf_counter()

    result = lookup(user_id)

    elapsed = (
        time.perf_counter() - start
    ) * 1000

    if result is None:
        raise RuntimeError(
            f"User {user_id} was not found"
        )

    latencies.append(elapsed)

print()
print("ArangoDB Lookup Benchmark Results")
print("----------------------------------")
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
print("ArangoDB lookup benchmark completed.")