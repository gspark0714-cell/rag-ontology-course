from owlready2 import *

# 1. 온톨로지 생성
onto = get_ontology("http://manufacturing.org/ontology#")

with onto:
    class 부품(Thing): pass
    class 대형부품(부품): pass
    class 제품(Thing): pass
    class 공정(Thing): pass

    class 포함한다(ObjectProperty):
        domain = [제품]
        range  = [부품]

    class 무게(DataProperty):
        domain = [부품]
        range  = [float]

    class 불량율(DataProperty):
        domain = [부품]
        range  = [float]

    # 2. 개체 생성
    모터   = 부품("모터");   모터.무게   = [5.0]
    케이싱 = 부품("케이싱"); 케이싱.무게 = [8.0]
    임펠러 = 부품("임펠러"); 임펠러.무게 = [2.0]
    베어링 = 부품("베어링"); 베어링.무게 = [0.5]; 베어링.불량율 = [0.05]
    샤프트 = 부품("샤프트"); 샤프트.무게 = [1.5]

    산업용펌프 = 제품("산업용펌프")
    산업용펌프.포함한다 = [모터, 임펠러, 케이싱]
    모터.포함한다 = [베어링, 샤프트]

    # 3. 대형부품 정의 — 무게 5kg 이상
    대형부품.equivalent_to = [
        부품 & 무게.some(float) & 무게.min(1, 5.0)
    ]

# 4. 추론 전
print("=== 추론 전 대형부품 ===")
for b in 대형부품.instances():
    print(f"  {b.name}")
print("(없음)")

# 5. HermiT 추론 실행
print("\n--- HermiT 추론 엔진 실행 중... ---")
try:
    sync_reasoner_hermit(infer_property_values=True)
    print("추론 완료!")

    # 6. 추론 후
    print("\n=== 추론 후 대형부품 ===")
    for b in 대형부품.instances():
        print(f"  ✓ {b.name} (무게: {b.무게[0]}kg)")

    print("\n=== 각 부품의 클래스 ===")
    for b in 부품.instances():
        classes = [c.name for c in b.is_a if hasattr(c, 'name')]
        print(f"  {b.name:10} 무게: {b.무게} → {classes}")

except Exception as e:
    print(f"추론 오류: {e}")