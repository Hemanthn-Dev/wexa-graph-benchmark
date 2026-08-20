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
    driver.verify_connectivity()
    print("✅ CognoDB connection successful!")
finally:
    driver.close()