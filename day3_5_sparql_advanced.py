from rdflib import Graph

g = Graph()
g.parse("d:/ontology/manufacturing_full.ttl", format="turtle")

# 1. 무게 조건 검색 (3kg 이상 부품만)
print("=" * 50)
print("1. 무게 3kg 이상 부품 조회")
print("=" * 50)
result = g.query("""
    PREFIX mfg: <http://manufacturing.org/ontology#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?이름 ?무게
    WHERE {
        ?부품 a mfg:부품 .
        ?부품 rdfs:label ?이름 .
        ?부품 mfg:무게 ?무게 .
        FILTER (?무게 >= 3.0)
    }
    ORDER BY DESC(?무게)
""")
for row in result:
    print(f"  {row.이름:10} {row.무게}kg")

# 2. 전체 부품 무게 합계
print("\n" + "=" * 50)
print("2. 전체 부품 무게 합계 및 평균")
print("=" * 50)
result = g.query("""
    PREFIX mfg: <http://manufacturing.org/ontology#>
    SELECT (SUM(?무게) AS ?합계) (AVG(?무게) AS ?평균) (COUNT(?부품) AS ?개수)
    WHERE {
        ?부품 a mfg:부품 .
        ?부품 mfg:무게 ?무게 .
    }
""")
for row in result:
    print(f"  부품 개수: {row.개수}개")
    print(f"  총 무게:   {float(row.합계):.1f}kg")
    print(f"  평균 무게: {float(row.평균):.2f}kg")

# 3. 2단계 이상 하위 부품 조회 (경로 탐색)
print("\n" + "=" * 50)
print("3. 산업용펌프의 모든 하위 부품 (몇 단계든)")
print("=" * 50)
result = g.query("""
    PREFIX mfg: <http://manufacturing.org/ontology#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT DISTINCT ?부품이름
    WHERE {
        mfg:산업용펌프 mfg:포함한다+ ?부품 .
        ?부품 rdfs:label ?부품이름 .
    }
""")
for row in result:
    print(f"  부품: {row.부품이름}")

# 4. 작업시간이 30분 이상인 공정
print("\n" + "=" * 50)
print("4. 작업시간 30분 이상 공정")
print("=" * 50)
result = g.query("""
    PREFIX mfg: <http://manufacturing.org/ontology#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?공정이름 ?시간
    WHERE {
        ?공정 a mfg:공정 .
        ?공정 rdfs:label ?공정이름 .
        ?공정 mfg:작업시간 ?시간 .
        FILTER (?시간 >= 30)
    }
    ORDER BY DESC(?시간)
""")
for row in result:
    print(f"  공정: {row.공정이름:12} 작업시간: {row.시간}분")

# 5. 불량이 있는 부품이 포함된 제품 찾기 (역방향 추적)
print("\n" + "=" * 50)
print("5. 불량 부품이 포함된 제품 추적")
print("=" * 50)
result = g.query("""
    PREFIX mfg: <http://manufacturing.org/ontology#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?제품이름 ?부품이름 ?불량이름
    WHERE {
        ?부품 mfg:발생한다 ?불량 .
        ?부품 rdfs:label ?부품이름 .
        ?불량 rdfs:label ?불량이름 .
        ?제품 mfg:포함한다+ ?부품 .
        ?제품 rdfs:label ?제품이름 .
    }
""")
for row in result:
    print(f"  제품: {row.제품이름} → 불량부품: {row.부품이름} → 불량: {row.불량이름}")