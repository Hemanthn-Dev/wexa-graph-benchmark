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

ITERATIONS = 20
USER_ID = "1"


def traversal(hops):

    if hops == 1:
        query = """
        FOR v IN 1..1 OUTBOUND
            @start
            connections
            RETURN v._key
        """

    elif hops == 2:
        query = """
        FOR v IN 1..2 OUTBOUND
            @start
            connections
            RETURN v._key
        """

    else:
        query = """
        FOR v IN 1..3 OUTBOUND
            @start
            connections
            RETURN v._key
        """

    cursor = db.aql.execute(
        query,
        bind_vars={
            "start": f"users/{USER_ID}"
        }
    )

    return len(list(cursor))


def percentile(values, p):

    values = sorted(values)

    index = (len(values) - 1) * p / 100

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


print("Starting ArangoDB traversal benchmark...")
print(f"User: {USER_ID}")
print(f"Iterations per hop: {ITERATIONS}")
print()

for hops in [3]:

    for _ in range(10):
        traversal(hops)

    print(f"Running {hops}-hop...")

    latencies = []
    results = 0

    for _ in range(ITERATIONS):

        start = time.perf_counter()

        results = traversal(hops)

        elapsed = (
            time.perf_counter() - start
        ) * 1000

        latencies.append(elapsed)

    print(
        f"{hops}-hop: "
        f"p50={percentile(latencies, 50):.3f} ms | "
        f"p95={percentile(latencies, 95):.3f} ms"
    )

    print()
    print(f"{hops}-hop results")
    print("----------------")
    print(f"Results found: {results}")
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

print("ArangoDB traversal benchmark completed.")