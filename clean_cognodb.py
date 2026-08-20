import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

uri = os.environ["COGNODB_URI"]
username = os.environ["COGNODB_USERNAME"]
password = os.environ["COGNODB_PASSWORD"]

driver = GraphDatabase.driver(
    uri,
    auth=(username, password)
)

try:
    with driver.session() as session:
        session.run("""
            MATCH (u:User)
            DETACH DELETE u
        """).consume()

    print("Benchmark data cleanup completed.")

finally:
    driver.close()