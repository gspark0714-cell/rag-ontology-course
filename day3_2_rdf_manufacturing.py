from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, OWL, XSD

g = Graph()
MFG = Namespace("http://manufacturing.org/ontology#")
g.bind("mfg", MFG)

# 1. 클래스 정의
classes = ["제품", "부품", "공정", "설비", "작업자", "불량"]
for c in classes:
    g.add((MFG[c], RDF.type, OWL.Class))

# 2. 계층 구조
g.add((MFG.부품, RDFS.subClassOf, MFG.제품))

# 3. 속성 정의
obj_props = ["포함한다", "사용한다", "담당한다", "발생한다"]
for p in obj_props:
    g.add((MFG[p], RDF.type, OWL.ObjectProperty))

data_props = ["무게", "제조사", "공정번호", "작업시간", "불량율"]
for p in data_props:
    g.add((MFG[p], RDF.type, OWL.DatatypeProperty))

# 4. 제품/부품 개체
products = [
    ("산업용펌프", "제품", 50.0),
    ("압력펌프",   "제품", 45.0),
    ("모터",      "부품", 5.0),
    ("임펠러",    "부품", 2.0),
    ("케이싱",    "부품", 8.0),
    ("베어링",    "부품", 0.5),
    ("샤프트",    "부품", 1.5),
]
for name, cls, weight in products:
    g.add((MFG[name], RDF.type, MFG[cls]))
    g.add((MFG[name], RDFS.label, Literal(name, lang="ko")))
    g.add((MFG[name], MFG.무게, Literal(weight, datatype=XSD.float)))

# 5. 부품 관계
relations = [
    ("산업용펌프", "모터"),
    ("산업용펌프", "임펠러"),
    ("산업용펌프", "케이싱"),
    ("모터",      "베어링"),
    ("모터",      "샤프트"),
]
for parent, child in relations:
    g.add((MFG[parent], MFG.포함한다, MFG[child]))

# 6. 공정 개체
processes = [
    ("조립공정1", "P001", 30),
    ("가공공정1", "P002", 60),
    ("검사공정1", "P003", 15),
]
for name, code, time in processes:
    g.add((MFG[name], RDF.type, MFG.공정))
    g.add((MFG[name], RDFS.label, Literal(name, lang="ko")))
    g.add((MFG[name], MFG.공정번호, Literal(code)))
    g.add((MFG[name], MFG.작업시간, Literal(time, datatype=XSD.integer)))

# 7. 설비 개체
equipments = ["선반기계A", "용접기B", "검사장비C"]
for eq in equipments:
    g.add((MFG[eq], RDF.type, MFG.설비))
    g.add((MFG[eq], RDFS.label, Literal(eq, lang="ko")))

# 8. 작업자 개체
workers = ["홍길동", "김철수", "이영희"]
for w in workers:
    g.add((MFG[w], RDF.type, MFG.작업자))
    g.add((MFG[w], RDFS.label, Literal(w, lang="ko")))

# 9. 공정-설비-작업자 연결
g.add((MFG.조립공정1, MFG.사용한다, MFG.선반기계A))
g.add((MFG.가공공정1, MFG.사용한다, MFG.용접기B))
g.add((MFG.검사공정1, MFG.사용한다, MFG.검사장비C))
g.add((MFG.조립공정1, MFG.담당한다, MFG.홍길동))
g.add((MFG.가공공정1, MFG.담당한다, MFG.김철수))
g.add((MFG.검사공정1, MFG.담당한다, MFG.이영희))

# 10. 불량 데이터 연결
g.add((MFG.불량001, RDF.type, MFG.불량))
g.add((MFG.불량001, RDFS.label, Literal("베어링 마모", lang="ko")))
g.add((MFG.불량001, MFG.불량율, Literal(0.05, datatype=XSD.float)))
g.add((MFG.베어링, MFG.발생한다, MFG.불량001))

# 11. 결과 출력
print(f"총 트리플 수: {len(g)}")
print(f"클래스 수: {len(classes)}")
print(f"제품/부품 수: {len(products)}")

# 12. 파일 저장 (3가지 형식)
g.serialize("d:/ontology/manufacturing_full.ttl", format="turtle")
g.serialize("d:/ontology/manufacturing_full.xml", format="xml")
g.serialize("d:/ontology/manufacturing_full.jsonld", format="json-ld")
print("\n--- 3가지 형식으로 저장 완료 ---")
print("  manufacturing_full.ttl    (Turtle 형식)")
print("  manufacturing_full.xml    (RDF/XML 형식)")
print("  manufacturing_full.jsonld (JSON-LD 형식)")