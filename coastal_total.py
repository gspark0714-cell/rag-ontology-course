from rdflib import Graph, Namespace, RDF, RDFS, OWL

# 그래프 생성 및 파일 로딩
g = Graph()
g.parse("coastal_total.ttl", format="turtle")

# 트리플 수 확인
print(f"로딩 완료. 트리플 수: {len(g)}")

# 예상 출력:
# 로딩 완료. 트리플 수: 287
# -> 클래스, 프로퍼티, Individual, Annotation 모두 포함한 숫자입니다
# -> 오늘 열심히 만든 것이 숫자로 나옵니다

from rdflib import Graph, Namespace, RDF, RDFS, OWL

g = Graph()
g.parse("coastal_total.ttl", format="turtle")

COASTAL = Namespace("http://www.example.org/coastal#")

print("=== 온톨로지의 모든 클래스 ===")
for cls in sorted(g.subjects(RDF.type, OWL.Class)):
    # 클래스 로컬명 (IRI에서 # 이후 부분)
    local_name = str(cls).split("#")[-1]
    
    # rdfs:label 조회 (한국어 우선)
    ko_label = None
    en_label = None
    for label in g.objects(cls, RDFS.label):
        if label.language == "ko":
            ko_label = str(label)
        elif label.language == "en":
            en_label = str(label)
    
    label_str = ko_label or en_label or ""
    print(f"  {local_name:<30} {label_str}")

# 예상 출력:
# === 온톨로지의 모든 클래스 ===
#   BreakwaterAccident             방파제사고
#   CoastalAccident                연안사고
#   CoastalActivityAccident        연안체험활동사고
#   CoastalLocation                연안지형
#   ...

def get_subclasses(graph, parent_class, indent=0):
    """재귀적으로 클래스 계층 출력"""
    for child in graph.subjects(RDFS.subClassOf, parent_class):
        local = str(child).split("#")[-1]
        label = graph.value(child, RDFS.label)
        label_str = f" ({label})" if label else ""
        print("  " * indent + f"├── {local}{label_str}")
        get_subclasses(graph, child, indent + 1)

OWL_THING = OWL.Thing
print("owl:Thing")
get_subclasses(g, OWL_THING)

# 예상 출력:
# owl:Thing
#   ├── CoastalAccident (연안사고)


query1 = """
PREFIX : <http://www.example.org/coastal#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?accident ?location ?locationName
WHERE {
    ?accident :occurredAt ?location .
    OPTIONAL { ?location :hasName ?locationName }
}
ORDER BY ?accident
"""

print("=== 연안사고와 발생장소 ===")
for row in g.query(query1):
    acc = str(row.accident).split("#")[-1]
    loc = str(row.location).split("#")[-1]
    loc_name = str(row.locationName) if row.locationName else ""
    print(f"  {acc:<25} -> {loc:<25} {loc_name}")


g.parse("coastal_total.ttl", format="turtle")
print(f"트리플 수: {len(g)}")