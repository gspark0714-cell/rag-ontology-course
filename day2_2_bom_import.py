from neo4j import GraphDatabase
import csv

driver = GraphDatabase.driver(
    "neo4j://127.0.0.1:7687",
    auth=("neo4j", "password123")
)

def import_bom(tx, row):
    # 부모 유형에 따라 라벨 구분
    if row['부모유형'] == '제품':
        tx.run("""
            MERGE (parent:제품 {code: $부모코드})
            SET parent.name = $부모이름
        """, 부모코드=row['부모코드'], 부모이름=row['부모이름'])
    else:
        tx.run("""
            MERGE (parent:부품 {code: $부모코드})
            SET parent.name = $부모이름
        """, 부모코드=row['부모코드'], 부모이름=row['부모이름'])

    # 자식 노드 생성
    if row['자식유형'] == '제품':
        tx.run("""
            MERGE (child:제품 {code: $자식코드})
            SET child.name = $자식이름
        """, 자식코드=row['자식코드'], 자식이름=row['자식이름'])
    else:
        tx.run("""
            MERGE (child:부품 {code: $자식코드})
            SET child.name = $자식이름
        """, 자식코드=row['자식코드'], 자식이름=row['자식이름'])

    # 관계 생성
    tx.run("""
        MATCH (parent {code: $부모코드})
        MATCH (child {code: $자식코드})
        MERGE (parent)-[:포함 {수량: $수량, 단위: $단위}]->(child)
    """,
    부모코드=row['부모코드'],
    자식코드=row['자식코드'],
    수량=int(row['수량']),
    단위=row['단위']
    )

with driver.session() as session:
    with open('d:/ontology/bom_data.csv', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            session.execute_write(import_bom, row)
            print(f"입력 완료: {row['부모이름']} → {row['자식이름']}")

print("--- 전체 BOM 데이터 입력 완료! ---")
driver.close()