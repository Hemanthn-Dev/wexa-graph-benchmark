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

        users = session.run("""
            MATCH (u:User)
            RETURN count(u) AS count
        """).single()["count"]

        relationships = session.run("""
            MATCH (:User)-[r:CONNECTED_TO]->(:User)
            RETURN count(r) AS count
        """).single()["count"]

        print("Current CognoDB state")
        print("---------------------")
        print(f"Users: {users}")
        print(f"Relationships: {relationships}")

finally:
    driver.close()