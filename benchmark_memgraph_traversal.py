import os
import time
import statistics

from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

URI = f"bolt+ssc://{os.environ['MEMGRAPH_HOST']}:{os.environ['MEMGRAPH_PORT']}"
USERNAME = os.environ["MEMGRAPH_USERNAME"]
PASSWORD = os.environ["MEMGRAPH_PASSWORD"]

USER_ID = "1"
ITERATIONS = 100

driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
)


def traversal(session, hops):

    if hops == 1:
        pattern = "(u:User {id: $user_id})-[:CONNECTED_TO]->(v:User)"
    elif hops == 2:
        pattern = "(u:User {id: $user_id})-[:CONNECTED_TO*2]->(v:User)"
    else:
        pattern = "(u:User {id: $user_id})-[:CONNECTED_TO*3]->(v:User)"

    result = session.run(
        f"""
        MATCH {pattern}
        RETURN count(v) AS results
        """,
        user_id=USER_ID
    )

    return result.single()["results"]


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


try:

    driver.verify_connectivity()

    print("Starting Memgraph traversal benchmark...")
    print(f"User: {USER_ID}")
    print(f"Iterations per hop: {ITERATIONS}")
    print()

    with driver.session() as session:

        for hops in [1, 2, 3]:

            latencies = []

            for _ in range(10):
                traversal(session, hops)

            print(f"Running {hops}-hop...")

            for _ in range(ITERATIONS):

                start = time.perf_counter()

                results = traversal(
                    session,
                    hops
                )

                elapsed = (
                    time.perf_counter()
                    - start
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

    print("Memgraph traversal benchmark completed.")

finally:

    driver.close()