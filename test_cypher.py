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

def main():
    with driver.session() as session:
        # Clean up anything from a previous test
        session.run("""
            MATCH (n)
            WHERE n.test_data = true
            DETACH DELETE n
        """)

        # Create two nodes and one relationship
        session.run("""
            CREATE (a:Person {
                name: 'Alice',
                test_data: true
            })
            CREATE (b:Person {
                name: 'Bob',
                test_data: true
            })
            CREATE (a)-[:FRIENDS_WITH]->(b)
        """)

        # Query the relationship
        result = session.run("""
            MATCH (a:Person)-[:FRIENDS_WITH]->(b:Person)
            WHERE a.test_data = true
            RETURN a.name AS person, b.name AS friend
        """)

        for record in result:
            print(f"{record['person']} is friends with {record['friend']}")

        # Clean up test data
        session.run("""
            MATCH (n)
            WHERE n.test_data = true
            DETACH DELETE n
        """)

if __name__ == "__main__":
    try:
        main()
        print("✅ Cypher test completed successfully!")
    finally:
        driver.close()