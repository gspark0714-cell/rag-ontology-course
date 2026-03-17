from neo4j import GraphDatabase

driver = GraphDatabase.driver(
    "bolt://127.0.0.1:7687",
    auth=("neo4j", "password123")
)

def clear_and_build(tx):
    # 기존 데이터 삭제
    tx.run("MATCH (n) DETACH DELETE n")

    # 1. 제품 노드
    tx.run("""
        CREATE (:제품 {name: '산업용펌프', code: 'PUMP-001', 무게: 50.0})
        CREATE (:제품 {name: '압력펌프', code: 'PUMP-002', 무게: 45.0})
    """)

    # 2. 부품 노드
    tx.run("""
        CREATE (:부품 {name: '모터', code: 'PART-001', 무게: 5.0, 불량율: 0.02})
        CREATE (:부품 {name: '임펠러', code: 'PART-002', 무게: 2.0, 불량율: 0.01})
        CREATE (:부품 {name: '케이싱', code: 'PART-003', 무게: 8.0, 불량율: 0.01})
        CREATE (:부품 {name: '베어링', code: 'PART-004', 무게: 0.5, 불량율: 0.05})
        CREATE (:부품 {name: '샤프트', code: 'PART-005', 무게: 1.5, 불량율: 0.01})
        CREATE (:부품 {name: '피스톤', code: 'PART-006', 무게: 3.0, 불량율: 0.03})
        CREATE (:부품 {name: '밸브', code: 'PART-007', 무게: 1.0, 불량율: 0.02})
    """)

    # 3. 공정 노드
    tx.run("""
        CREATE (:공정 {name: '조립공정1', code: 'PROC-001', 작업시간: 30})
        CREATE (:공정 {name: '가공공정1', code: 'PROC-002', 작업시간: 60})
        CREATE (:공정 {name: '검사공정1', code: 'PROC-003', 작업시간: 15})
    """)

    # 4. 설비 노드
    tx.run("""
        CREATE (:설비 {name: '선반기계A', code: 'EQ-001', 가동률: 0.85})
        CREATE (:설비 {name: '용접기B', code: 'EQ-002', 가동률: 0.90})
        CREATE (:설비 {name: '검사장비C', code: 'EQ-003', 가동률: 0.95})
    """)

    # 5. 작업자 노드
    tx.run("""
        CREATE (:작업자 {name: '홍길동', code: 'EMP-001', 직급: '중급'})
        CREATE (:작업자 {name: '김철수', code: 'EMP-002', 직급: '고급'})
        CREATE (:작업자 {name: '이영희', code: 'EMP-003', 직급: '초급'})
    """)

    # 6. 불량 이력 노드
    tx.run("""
        CREATE (:불량 {name: '베어링마모', code: 'DEF-001', 발생일: '2024-01-15', 심각도: '높음'})
        CREATE (:불량 {name: '피스톤균열', code: 'DEF-002', 발생일: '2024-02-20', 심각도: '중간'})
    """)

def create_relations(tx):
    # 제품-부품 포함 관계
    tx.run("""
        MATCH (p:제품 {name: '산업용펌프'}), (b:부품 {name: '모터'}) CREATE (p)-[:포함 {수량:1}]->(b)
        """)
    tx.run("""
        MATCH (p:제품 {name: '산업용펌프'}), (b:부품 {name: '임펠러'}) CREATE (p)-[:포함 {수량:1}]->(b)
        """)
    tx.run("""
        MATCH (p:제품 {name: '산업용펌프'}), (b:부품 {name: '케이싱'}) CREATE (p)-[:포함 {수량:1}]->(b)
        """)
    tx.run("""
        MATCH (p:부품 {name: '모터'}), (b:부품 {name: '베어링'}) CREATE (p)-[:포함 {수량:2}]->(b)
        """)
    tx.run("""
        MATCH (p:부품 {name: '모터'}), (b:부품 {name: '샤프트'}) CREATE (p)-[:포함 {수량:1}]->(b)
        """)
    tx.run("""
        MATCH (p:제품 {name: '압력펌프'}), (b:부품 {name: '피스톤'}) CREATE (p)-[:포함 {수량:4}]->(b)
        """)
    tx.run("""
        MATCH (p:제품 {name: '압력펌프'}), (b:부품 {name: '모터'}) CREATE (p)-[:포함 {수량:1}]->(b)
        """)
    tx.run("""
        MATCH (p:제품 {name: '압력펌프'}), (b:부품 {name: '밸브'}) CREATE (p)-[:포함 {수량:2}]->(b)
        """)

    # 공정-설비 관계
    tx.run("""
        MATCH (p:공정 {name: '조립공정1'}), (e:설비 {name: '선반기계A'}) CREATE (p)-[:사용]->(e)
        """)
    tx.run("""
        MATCH (p:공정 {name: '가공공정1'}), (e:설비 {name: '용접기B'}) CREATE (p)-[:사용]->(e)
        """)
    tx.run("""
        MATCH (p:공정 {name: '검사공정1'}), (e:설비 {name: '검사장비C'}) CREATE (p)-[:사용]->(e)
        """)

    # 공정-작업자 관계
    tx.run("""
        MATCH (p:공정 {name: '조립공정1'}), (w:작업자 {name: '홍길동'}) CREATE (p)-[:담당]->(w)
        """)
    tx.run("""
        MATCH (p:공정 {name: '가공공정1'}), (w:작업자 {name: '김철수'}) CREATE (p)-[:담당]->(w)
        """)
    tx.run("""
        MATCH (p:공정 {name: '검사공정1'}), (w:작업자 {name: '이영희'}) CREATE (p)-[:담당]->(w)
        """)

    # 부품-불량 관계
    tx.run("""
        MATCH (b:부품 {name: '베어링'}), (d:불량 {name: '베어링마모'}) CREATE (b)-[:불량발생]->(d)
        """)
    tx.run("""
        MATCH (b:부품 {name: '피스톤'}), (d:불량 {name: '피스톤균열'}) CREATE (b)-[:불량발생]->(d)
        """)

with driver.session() as session:
    session.execute_write(clear_and_build)
    session.execute_write(create_relations)

print("=== 5일차 Neo4j 데이터 구축 완료 ===")

# 통계 출력
with driver.session() as session:
    result = session.run("MATCH (n) RETURN labels(n)[0] AS 유형, COUNT(n) AS 개수")
    print("\n노드 통계:")
    for r in result:
        print(f"  {r['유형']:10}: {r['개수']}개")

    result = session.run("MATCH ()-[r]->() RETURN type(r) AS 관계, COUNT(r) AS 개수")
    print("\n관계 통계:")
    for r in result:
        print(f"  {r['관계']:10}: {r['개수']}개")

driver.close()