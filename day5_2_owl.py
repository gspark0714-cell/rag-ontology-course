from owlready2 import *
from neo4j import GraphDatabase

# 1. Neo4j 연결
driver = GraphDatabase.driver(
    "bolt://127.0.0.1:7687",
    auth=("neo4j", "password123")
)

# 2. 온톨로지 생성
onto = get_ontology("http://manufacturing.org/day5#")

with onto:
    class 제품(Thing): pass
    class 부품(Thing): pass
    class 공정(Thing): pass
    class 설비(Thing): pass
    class 작업자(Thing): pass
    class 불량(Thing): pass
    class 고위험부품(부품): pass
    class 핵심부품(부품): pass

    class 포함한다(ObjectProperty):
        domain = [제품]; range = [부품]
    class 불량발생(ObjectProperty):
        domain = [부품]; range = [불량]
    class 무게(DataProperty):
        domain = [부품]; range = [float]
    class 불량율(DataProperty):
        domain = [부품]; range = [float]
    class 점검필요(DataProperty):
        domain = [부품]; range = [bool]

# 3. Neo4j에서 데이터 읽어서 OWL에 자동 입력
print("=== Neo4j → OWL 자동 변환 ===")

with driver.session() as session:
    # 부품 데이터 읽기
    result = session.run("MATCH (b:부품) RETURN b.name AS name, b.무게 AS 무게, b.불량율 AS 불량율")
    with onto:
        for r in result:
            b = onto.부품(r['name'])
            if r['무게']: b.무게 = [float(r['무게'])]
            if r['불량율']: b.불량율 = [float(r['불량율'])]
            print(f"  부품 추가: {r['name']}")

    # 제품 데이터 읽기
    result = session.run("MATCH (p:제품) RETURN p.name AS name")
    with onto:
        for r in result:
            onto.제품(r['name'])
            print(f"  제품 추가: {r['name']}")

    # 포함 관계 읽기
    result = session.run("""
        MATCH (a)-[:포함]->(b:부품)
        RETURN a.name AS 부모, b.name AS 자식
    """)
    with onto:
        for r in result:
            부모 = onto[r['부모']]
            자식 = onto[r['자식']]
            if 부모 and 자식:
                if not hasattr(부모, '포함한다') or 자식 not in 부모.포함한다:
                    부모.포함한다.append(자식)

# 4. SWRL 규칙 적용
print("\n=== SWRL 규칙 적용 ===")

# 규칙 1: 불량율 > 3% → 고위험부품
print("\n[규칙 1] 불량율 > 3% → 고위험부품")
for b in onto.부품.instances():
    if b.불량율 and b.불량율[0] > 0.03:
        b.is_a.append(onto.고위험부품)
        b.점검필요 = [True]
        print(f"  ✓ {b.name} (불량율: {b.불량율[0]*100:.1f}%)")

# 규칙 2: 2개 이상 제품에 사용 → 핵심부품
print("\n[규칙 2] 2개 이상 제품에 사용 → 핵심부품")
부품사용횟수 = {}
for 제품 in onto.제품.instances():
    for 부품 in 제품.포함한다:
        부품사용횟수[부품] = 부품사용횟수.get(부품, 0) + 1
for 부품, 횟수 in 부품사용횟수.items():
    if 횟수 >= 2:
        부품.is_a.append(onto.핵심부품)
        print(f"  ✓ {부품.name} (사용횟수: {횟수}개 제품)")

# 5. 결과 출력
print("\n=== 분류 결과 ===")
print(f"  고위험부품: {[b.name for b in onto.고위험부품.instances()]}")
print(f"  핵심부품:   {[b.name for b in onto.핵심부품.instances()]}")

# 6. OWL 저장
onto.save("d:/ontology/day5.owl")
print("\n--- day5.owl 저장 완료 ---")
driver.close()