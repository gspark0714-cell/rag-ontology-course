from neo4j import GraphDatabase

driver = GraphDatabase.driver(
    "neo4j://127.0.0.1:7687",
    auth=("neo4j", "password123")
)

with driver.session() as session:
    result = session.run("RETURN 'Neo4j 연결 성공!' AS message")
    print(result.single()["message"])

driver.close()