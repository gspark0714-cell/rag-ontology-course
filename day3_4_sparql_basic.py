from rdflib import Graph
from rdflib.namespace import RDF, RDFS

# 데이터 로드
g = Graph()
g.parse("d:/ontology/manufacturing_full.ttl", format="turtle")
print(f"로드된 트리플 수: {len(g)}\n")

MFG = "http://manufacturing.org/ontology#"

# 1. 모든 제품 조회
print("=" * 50)
print("1. 모든 제품 조회")
print("=" * 50)
result = g.query("""
    PREFIX mfg: <http://manufacturing.org/ontology#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?이름
    WHERE {
        ?제품 a mfg:제품 .
        ?제품 rdfs:label ?이름 .
    }
""")
for row in result:
    print(f"  제품: {row.이름}")

# 2. 모든 부품 조회
print("\n" + "=" * 50)
print("2. 모든 부품 조회")
print("=" * 50)
result = g.query("""
    PREFIX mfg: <http://manufacturing.org/ontology#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?이름 ?무게
    WHERE {
        ?부품 a mfg:부품 .
        ?부품 rdfs:label ?이름 .
        ?부품 mfg:무게 ?무게 .
    }
    ORDER BY ?무게
""")
for row in result:
    print(f"  부품: {row.이름:10} 무게: {row.무게}kg")

# 3. 산업용펌프의 직속 부품 조회
print("\n" + "=" * 50)
print("3. 산업용펌프의 직속 부품 조회")
print("=" * 50)
result = g.query("""
    PREFIX mfg: <http://manufacturing.org/ontology#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?부품이름
    WHERE {
        mfg:산업용펌프 mfg:포함한다 ?부품 .
        ?부품 rdfs:label ?부품이름 .
    }
""")
for row in result:
    print(f"  부품: {row.부품이름}")

# 4. 공정-설비-작업자 한번에 조회
print("\n" + "=" * 50)
print("4. 공정-설비-작업자 연결 조회")
print("=" * 50)
result = g.query("""
    PREFIX mfg: <http://manufacturing.org/ontology#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?공정이름 ?설비이름 ?작업자이름
    WHERE {
        ?공정 a mfg:공정 .
        ?공정 rdfs:label ?공정이름 .
        ?공정 mfg:사용한다 ?설비 .
        ?설비 rdfs:label ?설비이름 .
        ?공정 mfg:담당한다 ?작업자 .
        ?작업자 rdfs:label ?작업자이름 .
    }
""")
for row in result:
    print(f"  공정: {row.공정이름:12} 설비: {row.설비이름:12} 작업자: {row.작업자이름}")

# 5. 불량 발생 부품 조회
print("\n" + "=" * 50)
print("5. 불량 발생 부품 조회")
print("=" * 50)
result = g.query("""
    PREFIX mfg: <http://manufacturing.org/ontology#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?부품이름 ?불량이름 ?불량율
    WHERE {
        ?부품 mfg:발생한다 ?불량 .
        ?부품 rdfs:label ?부품이름 .
        ?불량 rdfs:label ?불량이름 .
        ?불량 mfg:불량율 ?불량율 .
    }
""")
for row in result:
    print(f"  부품: {row.부품이름} → 불량: {row.불량이름} (불량율: {row.불량율})")