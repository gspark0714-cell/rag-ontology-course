from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, OWL, XSD

# 1. 그래프 생성
g = Graph()

# 2. 네임스페이스 정의 (우리만의 주소 체계)
MFG = Namespace("http://manufacturing.org/ontology#")
g.bind("mfg", MFG)

# 3. 제품/부품 클래스 정의
g.add((MFG.제품, RDF.type, OWL.Class))
g.add((MFG.부품, RDF.type, OWL.Class))
g.add((MFG.부품, RDFS.subClassOf, MFG.제품))

# 4. 속성 정의
g.add((MFG.포함한다, RDF.type, OWL.ObjectProperty))
g.add((MFG.무게, RDF.type, OWL.DatatypeProperty))
g.add((MFG.제조사, RDF.type, OWL.DatatypeProperty))

# 5. 개체(Individual) 추가
g.add((MFG.산업용펌프, RDF.type, MFG.제품))
g.add((MFG.산업용펌프, RDFS.label, Literal("산업용펌프", lang="ko")))
g.add((MFG.산업용펌프, MFG.무게, Literal(50.0, datatype=XSD.float)))

g.add((MFG.모터, RDF.type, MFG.부품))
g.add((MFG.모터, RDFS.label, Literal("모터", lang="ko")))
g.add((MFG.모터, MFG.무게, Literal(5.0, datatype=XSD.float)))
g.add((MFG.모터, MFG.제조사, Literal("현대전자")))

g.add((MFG.베어링, RDF.type, MFG.부품))
g.add((MFG.베어링, RDFS.label, Literal("베어링", lang="ko")))

g.add((MFG.샤프트, RDF.type, MFG.부품))
g.add((MFG.샤프트, RDFS.label, Literal("샤프트", lang="ko")))

# 6. 관계 추가
g.add((MFG.산업용펌프, MFG.포함한다, MFG.모터))
g.add((MFG.모터, MFG.포함한다, MFG.베어링))
g.add((MFG.모터, MFG.포함한다, MFG.샤프트))

# 7. 트리플 수 확인
print(f"총 트리플 수: {len(g)}")

# 8. 전체 트리플 출력
print("\n--- 전체 트리플 ---")
for s, p, o in g:
    print(f"  주어: {s.split('#')[-1]:15} 서술어: {p.split('#')[-1]:15} 목적어: {str(o).split('#')[-1]}")

# 9. Turtle 형식으로 저장
g.serialize("d:/ontology/manufacturing.ttl", format="turtle")
print("\n--- manufacturing.ttl 파일 저장 완료 ---")