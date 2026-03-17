from owlready2 import *

# 1. 온톨로지 생성
onto = get_ontology("http://manufacturing.org/ontology#")

with onto:
    # 2. 클래스 정의
    class 제품(Thing): pass
    class 부품(Thing): pass
    class 공정(Thing): pass
    class 설비(Thing): pass
    class 작업자(Thing): pass
    class 대형부품(부품): pass  # 부품의 하위 클래스

    # 3. 클래스 간 제약조건 (Disjoint — 제품과 공정은 서로 다른 개념)
    AllDisjoint([제품, 공정, 설비, 작업자])

    # 4. Object Property (관계) 정의
    class 포함한다(ObjectProperty):
        domain = [제품]   # 주어는 반드시 제품
        range  = [부품]   # 목적어는 반드시 부품

    class 사용한다(ObjectProperty):
        domain = [공정]
        range  = [설비]

    class 담당한다(ObjectProperty):
        domain = [공정]
        range  = [작업자]

    # 5. Data Property (속성) 정의
    class 무게(DataProperty):
        domain = [부품]
        range  = [float]

    class 작업시간(DataProperty):
        domain = [공정]
        range  = [int]

    class 불량율(DataProperty):
        domain = [부품]
        range  = [float]

    # 6. 개체(Individual) 생성
    산업용펌프 = 제품("산업용펌프")
    압력펌프   = 제품("압력펌프")

    모터   = 부품("모터");   모터.무게   = [5.0]
    임펠러 = 부품("임펠러"); 임펠러.무게 = [2.0]
    케이싱 = 부품("케이싱"); 케이싱.무게 = [8.0]
    베어링 = 부품("베어링"); 베어링.무게 = [0.5]; 베어링.불량율 = [0.05]
    샤프트 = 부품("샤프트"); 샤프트.무게 = [1.5]

    # 7. 관계 설정
    산업용펌프.포함한다 = [모터, 임펠러, 케이싱]
    모터.포함한다       = [베어링, 샤프트]

    # 8. 공정 개체
    조립공정1 = 공정("조립공정1"); 조립공정1.작업시간 = [30]
    가공공정1 = 공정("가공공정1"); 가공공정1.작업시간 = [60]
    검사공정1 = 공정("검사공정1"); 검사공정1.작업시간 = [15]

    # 9. 설비 개체
    선반기계A = 설비("선반기계A")
    용접기B   = 설비("용접기B")
    검사장비C = 설비("검사장비C")

    # 10. 공정-설비 연결
    조립공정1.사용한다 = [선반기계A]
    가공공정1.사용한다 = [용접기B]
    검사공정1.사용한다 = [검사장비C]

# 11. 결과 출력
print("=== OWL 온톨로지 생성 완료 ===")
print(f"클래스 수: {len(list(onto.classes()))}")
print(f"개체 수: {len(list(onto.individuals()))}")
print(f"속성 수: {len(list(onto.properties()))}")

print("\n--- 클래스 목록 ---")
for cls in onto.classes():
    print(f"  {cls.name}")

print("\n--- 제품 목록 ---")
for p in 제품.instances():
    print(f"  {p.name} → 포함 부품: {[b.name for b in p.포함한다]}")

print("\n--- 부품 무게 ---")
for b in 부품.instances():
    print(f"  {b.name:10} 무게: {b.무게}")

# 12. OWL 파일 저장
onto.save("d:/ontology/manufacturing.owl")
print("\n--- manufacturing.owl 저장 완료 ---")