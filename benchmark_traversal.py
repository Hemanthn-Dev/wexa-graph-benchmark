import os
import time
import statistics

from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

URI = os.environ["COGNODB_URI"]
USERNAME = os.environ["COGNODB_USERNAME"]
PASSWORD = os.environ["COGNODB_PASSWORD"]

USER_ID = "1"
ITERATIONS = 100

driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
)


QUERIES = {
    "1-hop": """
        MATCH (u:User {id: $user_id})
              -[:CONNECTED_TO]->(v:User)
        RETURN count(v) AS result
    """,

    "2-hop": """
        MATCH (u:User {id: $user_id})
              -[:CONNECTED_TO]->(v:User)
              -[:CONNECTED_TO]->(w:User)
        RETURN count(w) AS result
    """,

    "3-hop": """
        MATCH (u:User {id: $user_id})
              -[:CONNECTED_TO]->(v:User)
              -[:CONNECTED_TO]->(w:User)
              -[:CONNECTED_TO]->(x:User)
        RETURN count(x) AS result
    """
}


def traversal(session, query):
    result = session.run(
        query,
        user_id=USER_ID
    )

    return result.single()["result"]


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


def benchmark_depth(session, name, query):

    # Warm-up
    for _ in range(10):
        traversal(session, query)

    latencies = []
    result_count = 0

    for _ in range(ITERATIONS):

        start = time.perf_counter()

        result_count = traversal(
            session,
            query
        )

        elapsed = (
            time.perf_counter() - start
        ) * 1000

        latencies.append(elapsed)

    return {
        "name": name,
        "result": result_count,
        "queries": len(latencies),
        "min": min(latencies),
        "average": statistics.mean(latencies),
        "p50": percentile(latencies, 50),
        "p95": percentile(latencies, 95),
        "max": max(latencies)
    }


try:

    driver.verify_connectivity()

    print("Starting traversal benchmark...")
    print(f"User: {USER_ID}")
    print(f"Iterations per hop: {ITERATIONS}")
    print()

    results = []

    with driver.session() as session:

        for name, query in QUERIES.items():

            print(f"Running {name}...")

            result = benchmark_depth(
                session,
                name,
                query
            )

            results.append(result)

            print(
                f"{name}: "
                f"p50={result['p50']:.3f} ms | "
                f"p95={result['p95']:.3f} ms"
            )

    print()
    print("Traversal benchmark results")
    print("---------------------------")

    for result in results:

        print()
        print(result["name"])

        print(
            f"Results found: "
            f"{result['result']:,}"
        )

        print(
            f"Queries: "
            f"{result['queries']}"
        )

        print(
            f"Min: "
            f"{result['min']:.3f} ms"
        )

        print(
            f"Average: "
            f"{result['average']:.3f} ms"
        )

        print(
            f"p50: "
            f"{result['p50']:.3f} ms"
        )

        print(
            f"p95: "
            f"{result['p95']:.3f} ms"
        )

        print(
            f"Max: "
            f"{result['max']:.3f} ms"
        )

    print()
    print("Traversal benchmark completed.")

finally:

    driver.close()