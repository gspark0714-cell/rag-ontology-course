from rdflib import Graph
import json

# 1. Turtle 파일 읽어서 내용 출력
print("=" * 50)
print("1. Turtle 형식 (.ttl) — 사람이 읽기 가장 쉬움")
print("=" * 50)
with open("d:/ontology/manufacturing_full.ttl", encoding="utf-8") as f:
    content = f.read()
    # 앞부분 20줄만 출력
    lines = content.split("\n")[:20]
    print("\n".join(lines))

# 2. RDF/XML 파일 읽어서 내용 출력
print("\n" + "=" * 50)
print("2. RDF/XML 형식 (.xml) — 시스템 간 데이터 교환용")
print("=" * 50)
with open("d:/ontology/manufacturing_full.xml", encoding="utf-8") as f:
    content = f.read()
    lines = content.split("\n")[:20]
    print("\n".join(lines))

# 3. JSON-LD 파일 읽어서 내용 출력
print("\n" + "=" * 50)
print("3. JSON-LD 형식 (.jsonld) — 웹 개발자 친화적")
print("=" * 50)
with open("d:/ontology/manufacturing_full.jsonld", encoding="utf-8") as f:
    content = f.read()
    lines = content.split("\n")[:20]
    print("\n".join(lines))

# 4. 파일 크기 비교
import os
files = [
    ("Turtle",   "d:/ontology/manufacturing_full.ttl"),
    ("RDF/XML",  "d:/ontology/manufacturing_full.xml"),
    ("JSON-LD",  "d:/ontology/manufacturing_full.jsonld"),
]
print("\n" + "=" * 50)
print("4. 파일 크기 비교")
print("=" * 50)
for name, path in files:
    size = os.path.getsize(path)
    print(f"  {name:10}: {size:,} bytes")

# 5. 세 파일 모두 동일한 트리플 수인지 확인
print("\n" + "=" * 50)
print("5. 트리플 수 확인 (세 형식 모두 동일해야 함)")
print("=" * 50)
for name, path in files:
    g = Graph()
    fmt = "turtle" if path.endswith(".ttl") else "xml" if path.endswith(".xml") else "json-ld"
    g.parse(path, format=fmt)
    print(f"  {name:10}: {len(g)}개 트리플")