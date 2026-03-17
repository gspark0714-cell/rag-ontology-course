from owlready2 import *

# 1. 온톨로지 로드
onto = get_ontology("d:/ontology/manufacturing.owl").load()

with onto:
    # 2. 추가 클래스 정의
    class 고위험부품(onto.부품): pass
    class 핵심부품(onto.부품): pass
    class 긴급점검공정(onto.공정): pass

    # 3. 추가 속성 정의
    class 점검필요(DataProperty):
        domain = [onto.부품]
        range  = [bool]

    class 우선순위(DataProperty):
        domain = [onto.부품]
        range  = [int]

# 4. SWRL 규칙을 Python으로 구현
print("=" * 50)
print("SWRL 규칙 기반 추론 시작")
print("=" * 50)

# 규칙 1: 불량율 > 3% AND 무게 > 3kg → 고위험부품
print("\n[규칙 1] 불량율 > 3% AND 무게 > 3kg → 고위험부품")
for b in onto.부품.instances():
    if b.불량율 and b.불량율[0] > 0.03:
        b.is_a.append(onto.고위험부품)
        b.점검필요 = [True]
        b.우선순위 = [1]
        print(f"  ✓ {b.name} → 고위험부품 (불량율:{b.불량율[0]*100}%, 무게:{b.무게[0]}kg)")

print("  부품 사용 현황:")
for 제품 in onto.제품.instances():
    print(f"    {제품.name} → {[b.name for b in 제품.포함한다]}")
    
# 규칙 2: 2개 이상 제품에 사용 → 핵심부품
print("\n[규칙 2] 2개 이상 제품에 사용 → 핵심부품")
부품사용횟수 = {}
for 제품 in onto.제품.instances():
    for 부품 in 제품.포함한다:
        부품사용횟수[부품] = 부품사용횟수.get(부품, 0) + 1

for 부품, 횟수 in 부품사용횟수.items():
    if 횟수 >= 2:
        부품.is_a.append(onto.핵심부품)
        부품.우선순위 = [1]
        print(f"  ✓ {부품.name} → 핵심부품 (사용횟수: {횟수}개 제품)")

# 규칙 3: 작업시간 > 45분 → 긴급점검공정
print("\n[규칙 3] 작업시간 > 45분 → 긴급점검공정")
for p in onto.공정.instances():
    if p.작업시간 and p.작업시간[0] > 45:
        p.is_a.append(onto.긴급점검공정)
        print(f"  ✓ {p.name} → 긴급점검공정 (작업시간: {p.작업시간[0]}분)")

# 규칙 4: 핵심부품 + 불량위험 → 즉시점검
print("\n[규칙 4] 핵심부품 + 불량위험 → 즉시점검")
for b in onto.부품.instances():
    is_핵심 = onto.핵심부품 in b.is_a
    is_불량위험 = b.불량율 and b.불량율[0] > 0.03
    if is_핵심 and is_불량위험:
        b.우선순위 = [0]
        print(f"  🚨 {b.name} → 즉시점검! (핵심부품 + 불량위험)")

# 5. 최종 점검 우선순위
print("\n" + "=" * 50)
print("최종 점검 우선순위")
print("=" * 50)
점검목록 = [
    (b, b.우선순위[0] if b.우선순위 else 99)
    for b in onto.부품.instances()
    if b.점검필요 and b.점검필요[0]
]
점검목록.sort(key=lambda x: x[1])

if 점검목록:
    for b, priority in 점검목록:
        클래스 = [c.name for c in b.is_a if hasattr(c, 'name')]
        print(f"  우선순위 {priority}: {b.name:10} {클래스}")
else:
    print("  점검 필요 부품 없음")

# 6. 저장
onto.save("d:/ontology/manufacturing_swrl.owl")
print("\n--- manufacturing_swrl.owl 저장 완료 ---")