from owlready2 import *

# 1. OWL 파일 로드
onto = get_ontology("d:/ontology/manufacturing_swrl.owl").load()

print("=" * 50)
print("심화 관계 탐색 및 분석")
print("=" * 50)

# 2. 전체 부품 계층 구조 출력 (재귀 탐색)
def print_tree(node, depth=0):
    indent = "  " * depth
    무게 = node.무게[0] if node.무게 else "?"
    불량 = f" ⚠불량율:{node.불량율[0]*100:.1f}%" if node.불량율 else ""
    print(f"{indent}{'└─' if depth > 0 else ''}{node.name} ({무게}kg){불량}")
    if hasattr(node, '포함한다'):
        for 하위 in node.포함한다:
            print_tree(하위, depth + 1)

print("\n1. 전체 BOM 계층 구조")
for 제품 in onto.제품.instances():
    print_tree(제품)

# 3. 불량 영향 분석 — 어떤 제품이 영향받나?
print("\n2. 불량 부품 영향 분석")
def find_affected_products(불량부품, 제품목록):
    영향제품 = []
    for 제품 in 제품목록:
        # 직접 포함
        if 불량부품 in 제품.포함한다:
            영향제품.append((제품.name, [불량부품.name]))
            continue
        # 2단계 포함
        for 중간 in 제품.포함한다:
            if hasattr(중간, '포함한다') and 불량부품 in 중간.포함한다:
                영향제품.append((제품.name, [중간.name, 불량부품.name]))
    return 영향제품

고위험부품목록 = [b for b in onto.부품.instances() if onto.고위험부품 in b.is_a]
제품목록 = list(onto.제품.instances())

for 불량부품 in 고위험부품목록:
    print(f"\n  불량부품: {불량부품.name} (불량율: {불량부품.불량율[0]*100:.1f}%)")
    영향 = find_affected_products(불량부품, 제품목록)
    if 영향:
        for 제품명, 경로 in 영향:
            경로str = " → ".join(경로)
            print(f"  영향 제품: {제품명} (경로: {경로str})")
    else:
        print("  영향받는 제품 없음")

# 4. 공정별 설비 및 작업자 분석
print("\n3. 공정별 설비 및 작업자 현황")
result = list(default_world.sparql("""
    PREFIX : <http://manufacturing.org/ontology#>
    SELECT ?공정 ?설비 ?작업시간
    WHERE {
        ?공정 a :공정 .
        ?공정 :사용한다 ?설비 .
        ?공정 :작업시간 ?작업시간 .
    }
    ORDER BY DESC(?작업시간)
"""))
for row in result:
    공정명 = str(row[0]).split('#')[-1].split('.')[-1]
    설비명 = str(row[1]).split('#')[-1].split('.')[-1]
    print(f"  공정: {공정명:12} 설비: {설비명:12} 작업시간: {row[2]}분")

# 5. 전체 온톨로지 통계
print("\n4. 온톨로지 통계")
print(f"  제품 수:     {len(list(onto.제품.instances()))}개")
print(f"  부품 수:     {len(list(onto.부품.instances()))}개")
print(f"  공정 수:     {len(list(onto.공정.instances()))}개")
print(f"  설비 수:     {len(list(onto.설비.instances()))}개")
print(f"  고위험부품:  {len(고위험부품목록)}개")
total_weight = sum(b.무게[0] for b in onto.부품.instances() if b.무게)
print(f"  전체 부품 무게: {total_weight:.1f}kg")