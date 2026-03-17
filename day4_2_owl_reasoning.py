from owlready2 import *

# 1. 온톨로지 로드
onto = get_ontology("d:/ontology/manufacturing.owl").load()

# 2. 추론 전 상태 출력
print("=== 추론 전 부품 목록 ===")
for b in onto.부품.instances():
    print(f"  {b.name:10} 무게: {b.무게}")

# 3. 규칙 기반 추론 — Python으로 직접 구현
print("\n--- 추론 규칙 적용 중... ---")
print("규칙 1: 무게 5kg 이상 → 대형부품")
print("규칙 2: 불량율 0.03 이상 → 불량위험부품")
print("규칙 3: 작업시간 30분 이상 → 장시간공정")

대형부품_목록 = []
불량위험_목록 = []

for b in onto.부품.instances():
    # 규칙 1: 무게 5kg 이상이면 대형부품
    if b.무게 and b.무게[0] >= 5.0:
        대형부품_목록.append(b)

    # 규칙 2: 불량율 3% 이상이면 불량위험부품
    if b.불량율 and b.불량율[0] >= 0.03:
        불량위험_목록.append(b)

장시간공정_목록 = []
for p in onto.공정.instances():
    # 규칙 3: 작업시간 30분 이상이면 장시간공정
    if p.작업시간 and p.작업시간[0] >= 30:
        장시간공정_목록.append(p)

# 4. 추론 결과 출력
print("\n=== 추론 결과 ===")

print("\n[규칙 1] 대형부품 (무게 5kg 이상):")
if 대형부품_목록:
    for b in 대형부품_목록:
        print(f"  ✓ {b.name} (무게: {b.무게[0]}kg)")
else:
    print("  해당 없음")

print("\n[규칙 2] 불량위험부품 (불량율 3% 이상):")
if 불량위험_목록:
    for b in 불량위험_목록:
        print(f"  ⚠ {b.name} (불량율: {b.불량율[0]*100:.1f}%)")
else:
    print("  해당 없음")

print("\n[규칙 3] 장시간공정 (작업시간 30분 이상):")
if 장시간공정_목록:
    for p in 장시간공정_목록:
        print(f"  ⏱ {p.name} (작업시간: {p.작업시간[0]}분)")
else:
    print("  해당 없음")

# 5. 불량 부품이 포함된 제품 역추적
print("\n=== 불량위험부품 역추적 ===")
print("불량위험부품이 포함된 제품 찾기:")
for 불량부품 in 불량위험_목록:
    for 제품 in onto.제품.instances():
        # 직접 포함 관계 확인
        if 불량부품 in 제품.포함한다:
            print(f"  {제품.name} → 직접포함 → {불량부품.name}")
        # 2단계 포함 관계 확인
        for 중간부품 in 제품.포함한다:
            if hasattr(중간부품, '포함한다') and 불량부품 in 중간부품.포함한다:
                print(f"  {제품.name} → {중간부품.name} → {불량부품.name} ⚠ 불량위험!")