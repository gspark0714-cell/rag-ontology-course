from owlready2 import *

# 1. OWL 파일 로드
onto = get_ontology("d:/ontology/manufacturing_swrl.owl").load()

print("=" * 50)
print("OWL + SPARQL 지식 탐색")
print("=" * 50)

# 2. 모든 부품과 무게 조회
print("\n1. 모든 부품과 무게 조회")
result = list(default_world.sparql("""
    PREFIX : <http://manufacturing.org/ontology#>
    SELECT ?부품 ?무게
    WHERE {
        ?부품 a :부품 .
        ?부품 :무게 ?무게 .
    }
    ORDER BY DESC(?무게)
"""))
for row in result:
    print(f"  {str(row[0]).split('#')[-1]:10} 무게: {row[1]}kg")

# 3. 고위험부품 조회
print("\n2. 고위험부품 조회")
result = list(default_world.sparql("""
    PREFIX : <http://manufacturing.org/ontology#>
    SELECT ?부품 ?불량율
    WHERE {
        ?부품 a :고위험부품 .
        ?부품 :불량율 ?불량율 .
    }
"""))
if result:
    for row in result:
        print(f"  ⚠ {str(row[0]).split('#')[-1]} (불량율: {float(row[1])*100:.1f}%)")
else:
    print("  없음")

# 4. 제품-부품 관계 조회
print("\n3. 제품-부품 관계 조회")
result = list(default_world.sparql("""
    PREFIX : <http://manufacturing.org/ontology#>
    SELECT ?제품 ?부품
    WHERE {
        ?제품 a :제품 .
        ?제품 :포함한다 ?부품 .
    }
"""))
for row in result:
    print(f"  {str(row[0]).split('#')[-1]} → {str(row[1]).split('#')[-1]}")

# 5. 점검 필요 부품 조회
print("\n4. 점검 필요 부품 조회")
result = list(default_world.sparql("""
    PREFIX : <http://manufacturing.org/ontology#>
    SELECT ?부품 ?우선순위
    WHERE {
        ?부품 :점검필요 true .
        ?부품 :우선순위 ?우선순위 .
    }
    ORDER BY ?우선순위
"""))
if result:
    for row in result:
        print(f"  우선순위 {row[1]}: {str(row[0]).split('#')[-1]}")
else:
    print("  없음")