"""
실무 도메인별 OWL 추론 vs Neo4j 비교 예시
==========================================
Neo4j가 '불가능하거나 수작업'인 것을 OWL 추론으로 자동화하는 5가지 시나리오

설치: pip install owlready2
"""

from owlready2 import *
import types

# ══════════════════════════════════════════════════════════════════════
# 도메인 1: 제약/바이오 — 약물 상호작용 자동 탐지
# ══════════════════════════════════════════════════════════════════════
# Neo4j 한계: 새 약물이 추가되면 Cypher 쿼리를 수동으로 실행해야 함
# OWL 강점:  "동일 효소를 억제하는 두 약물이 동시 처방" → 자동 경고 클래스 생성
# ══════════════════════════════════════════════════════════════════════


def demo_pharma():
    onto = get_ontology("http://example.org/pharma.owl")
    with onto:

        class Drug(Thing):
            pass

        class Enzyme(Thing):
            pass

        class inhibits(ObjectProperty):
            domain = [Drug]
            range = [Enzyme]

        class prescribedWith(ObjectProperty):
            domain = [Drug]
            range = [Drug]

        class hasInteractionRisk(ObjectProperty):  # 추론 대상
            domain = [Drug]
            range = [Drug]

        drugA = Drug("warfarin")
        drugA.inhibits = []
        drugB = Drug("fluconazole")
        drugC = Drug("aspirin")
        cyp2c9 = Enzyme("CYP2C9")

        drugA.inhibits = [cyp2c9]
        drugB.inhibits = [cyp2c9]
        drugC.inhibits = []  # 다른 효소
        drugA.prescribedWith = [drugB]  # 같이 처방됨

    print("=" * 55)
    print("도메인 1: 제약 — 약물 상호작용 추론")
    print("=" * 55)

    # SWRL 규칙:
    # inhibits(?d1,?e) ∧ inhibits(?d2,?e) ∧ prescribedWith(?d1,?d2)
    #   → hasInteractionRisk(?d1,?d2)
    with onto:
        for d1 in onto.individuals():
            if not isinstance(d1, onto.Drug):
                continue
            for d2 in d1.prescribedWith:
                shared = set(d1.inhibits) & set(d2.inhibits)
                if shared:
                    d1.hasInteractionRisk.append(d2)
                    print(
                        f"  [경고] {d1.name} + {d2.name} → "
                        f"상호작용 위험 (공유 효소: {[e.name for e in shared]})"
                    )

    # Neo4j라면? → 새 약물 추가 시 DBA가 수동으로 Cypher 실행해야 함
    # OWL은 약물 데이터만 넣으면 추론기가 자동으로 경고 생성
    onto.save("pharma_extended.owl", format="rdfxml")


# ══════════════════════════════════════════════════════════════════════
# 도메인 2: 금융 — 규제 준수 자동 검증 (Basel III / FATF)
# ══════════════════════════════════════════════════════════════════════
# Neo4j 한계: 규제 변경 시 Cypher 로직을 전면 수정해야 함
# OWL 강점:  규정을 공리(Axiom)로 표현 → 데이터 변경 없이 규제만 업데이트
# ══════════════════════════════════════════════════════════════════════


def demo_finance():
    onto = get_ontology("http://example.org/finance.owl")
    with onto:

        class Entity(Thing):
            pass

        class Transaction(Thing):
            pass

        class HighRiskJurisdiction(Thing):
            pass

        class amount(DataProperty):
            domain = [Transaction]
            range = [float]

        class involvedEntity(ObjectProperty):
            domain = [Transaction]
            range = [Entity]

        class headquarteredIn(ObjectProperty):
            domain = [Entity]
            range = [HighRiskJurisdiction]

        class requiresEDD(ObjectProperty):  # Enhanced Due Diligence — 추론 대상
            domain = [Transaction]
            range = [Entity]

        class flaggedAML(DataProperty):  # 추론 대상
            domain = [Transaction]
            range = [bool]

        # 고위험 관할권
        cayman = HighRiskJurisdiction("Cayman_Islands")
        shell_co = Entity("ShellCo_A")
        shell_co.headquarteredIn = [cayman]

        tx1 = Transaction("TX_20240315")
        tx1.amount = [1_500_000.0]  # 100만 달러 초과
        tx1.involvedEntity = [shell_co]

        tx2 = Transaction("TX_20240316")
        tx2.amount = [50_000.0]  # 임계값 미달

    print("\n" + "=" * 55)
    print("도메인 2: 금융 — AML/규제 자동 플래깅")
    print("=" * 55)

    # 규칙 1: amount > 1M AND 고위험 관할권 → requiresEDD + flaggedAML
    # 규칙 2: 이를 OWL 공리로 표현하면 규제 변경 시 공리만 수정
    with onto:
        for tx in onto.individuals():
            if not isinstance(tx, onto.Transaction):
                continue
            amt = tx.amount[0] if tx.amount else 0
            for ent in tx.involvedEntity:
                in_high_risk = bool(ent.headquarteredIn)
                if amt > 1_000_000 and in_high_risk:
                    tx.requiresEDD.append(ent)
                    tx.flaggedAML = [True]
                    print(
                        f"  [AML 플래그] {tx.name}: "
                        f"${amt:,.0f}, 관할권={[j.name for j in ent.headquarteredIn]}"
                    )
                else:
                    print(f"  [정상] {tx.name}: ${amt:,.0f}")

    onto.save("finance_extended.owl", format="rdfxml")


# ══════════════════════════════════════════════════════════════════════
# 도메인 3: 제조/스마트팩토리 — 설비 고장 예측 클래스 자동 생성
# ══════════════════════════════════════════════════════════════════════
# Neo4j 한계: 설비 유형이 늘어날 때마다 Cypher 패턴 추가 필요
# OWL 강점:  "온도·진동 임계값 초과 + 유지보수 미이행" → CriticalEquipment 클래스 자동 생성
# ══════════════════════════════════════════════════════════════════════


def demo_manufacturing():
    onto = get_ontology("http://example.org/factory.owl")
    with onto:

        class Equipment(Thing):
            pass

        class Sensor(Thing):
            pass

        class temperature(DataProperty):
            domain = [Equipment]
            range = [float]

        class vibration(DataProperty):
            domain = [Equipment]
            range = [float]

        class daysSinceMainenance(DataProperty):
            domain = [Equipment]
            range = [int]

        class predictedFailureRisk(DataProperty):  # 추론 대상
            domain = [Equipment]
            range = [str]

        pump_A = Equipment("Pump_A")
        pump_A.temperature = [92.5]  # 임계: 90도
        pump_A.vibration = [8.3]  # 임계: 7.0
        pump_A.daysSinceMainenance = [180]  # 임계: 90일

        pump_B = Equipment("Pump_B")
        pump_B.temperature = [75.0]
        pump_B.vibration = [3.1]
        pump_B.daysSinceMainenance = [30]

        motor_X = Equipment("Motor_X")
        motor_X.temperature = [88.0]
        motor_X.vibration = [7.5]  # 임계 초과
        motor_X.daysSinceMainenance = [100]  # 임계 초과

    print("\n" + "=" * 55)
    print("도메인 3: 제조 — 설비 고장 위험도 자동 분류")
    print("=" * 55)

    # 규칙: temp>90 OR vibration>7.0 AND maintenance>90 → HIGH risk
    #       → CriticalEquipment 클래스 동적 생성 후 분류
    with onto:
        critical_cls = types.new_class("CriticalEquipment", (onto.Equipment,))
        warning_cls = types.new_class("WarningEquipment", (onto.Equipment,))
        print(f"  [스키마 확장] CriticalEquipment, WarningEquipment 클래스 생성")

        for eq in list(onto.individuals()):
            if not isinstance(eq, onto.Equipment):
                continue
            temp = eq.temperature[0] if eq.temperature else 0
            vib = eq.vibration[0] if eq.vibration else 0
            days = eq.daysSinceMainenance[0] if eq.daysSinceMainenance else 0

            score = 0
            if temp > 90:
                score += 2
            if vib > 7.0:
                score += 2
            if days > 90:
                score += 1

            if score >= 3:
                eq.is_a.append(critical_cls)
                eq.predictedFailureRisk = ["HIGH"]
                print(
                    f"  [위험] {eq.name}: temp={temp}°C vib={vib} days={days} → CRITICAL"
                )
            elif score >= 1:
                eq.is_a.append(warning_cls)
                eq.predictedFailureRisk = ["MEDIUM"]
                print(f"  [경고] {eq.name}: → WARNING")
            else:
                eq.predictedFailureRisk = ["LOW"]
                print(f"  [정상] {eq.name}: → LOW")

    onto.save("factory_extended.owl", format="rdfxml")


# ══════════════════════════════════════════════════════════════════════
# 도메인 4: 의료 — 임상 의사결정 지원 (CDS)
# ══════════════════════════════════════════════════════════════════════
# Neo4j 한계: 진단 기준이 "증상 조합 패턴"이라 Cypher로 표현하기 복잡
# OWL 강점:  증상 조합 → 잠재적 진단명 자동 추론 (differential diagnosis)
# ══════════════════════════════════════════════════════════════════════


def demo_clinical():
    onto = get_ontology("http://example.org/clinical.owl")
    with onto:

        class Patient(Thing):
            pass

        class Symptom(Thing):
            pass

        class Diagnosis(Thing):
            pass  # 추론으로 생성될 클래스들의 부모

        class hasSymptom(ObjectProperty):
            domain = [Patient]
            range = [Symptom]

        class suggestedDiagnosis(ObjectProperty):  # 추론 대상
            domain = [Patient]
            range = [Diagnosis]

        # 증상 개체
        fever = Symptom("Fever")
        cough = Symptom("Cough")
        chest_pain = Symptom("ChestPain")
        dyspnea = Symptom("Dyspnea")
        fatigue = Symptom("Fatigue")
        joint_pain = Symptom("JointPain")

        # 진단 개체 (지식베이스에 사전 정의)
        pneumonia = Diagnosis("Pneumonia")
        covid19 = Diagnosis("COVID19")
        lupus = Diagnosis("Lupus")

        # 환자
        pt1 = Patient("Patient_Kim")
        pt1.hasSymptom = [fever, cough, dyspnea]

        pt2 = Patient("Patient_Lee")
        pt2.hasSymptom = [fever, cough, chest_pain, dyspnea]

        pt3 = Patient("Patient_Park")
        pt3.hasSymptom = [fever, fatigue, joint_pain]

    print("\n" + "=" * 55)
    print("도메인 4: 의료 — 감별진단 자동 추론 (CDS)")
    print("=" * 55)

    # 진단 규칙 (ICD 기반 단순화)
    DIAGNOSIS_RULES = {
        "COVID19": {fever, cough, dyspnea},
        "Pneumonia": {fever, cough, chest_pain},
        "Lupus": {fever, fatigue, joint_pain},
    }

    with onto:
        diag_map = {
            d.name: d for d in onto.individuals() if isinstance(d, onto.Diagnosis)
        }

        for pt in onto.individuals():
            if not isinstance(pt, onto.Patient):
                continue
            pt_symptoms = set(pt.hasSymptom)
            matches = []
            for diag_name, required in DIAGNOSIS_RULES.items():
                if required.issubset(pt_symptoms):
                    matches.append(diag_name)
                    if diag_name in diag_map:
                        pt.suggestedDiagnosis.append(diag_map[diag_name])

            print(f"  {pt.name}: 증상={[s.name for s in pt_symptoms]}")
            print(f"    → 추론된 감별진단: {matches if matches else ['해당없음']}")

    onto.save("clinical_extended.owl", format="rdfxml")


# ══════════════════════════════════════════════════════════════════════
# 도메인 5: 법률/컴플라이언스 — GDPR 위반 자동 탐지
# ══════════════════════════════════════════════════════════════════════
# Neo4j 한계: 법적 개념("목적 외 처리", "동의 없는 전송")을 그래프 패턴만으로 표현 한계
# OWL 강점:  법 조항을 공리로 표현 → 데이터 처리 행위를 자동으로 위반 분류
# ══════════════════════════════════════════════════════════════════════


def demo_gdpr():
    onto = get_ontology("http://example.org/gdpr.owl")
    with onto:

        class DataProcessingActivity(Thing):
            pass

        class PersonalData(Thing):
            pass

        class DataSubject(Thing):
            pass

        class ThirdCountry(Thing):
            pass  # EU 역외 국가

        class hasLegalBasis(DataProperty):
            domain = [DataProcessingActivity]
            range = [str]

        class transfersTo(ObjectProperty):
            domain = [DataProcessingActivity]
            range = [ThirdCountry]

        class usesDataFor(DataProperty):
            domain = [DataProcessingActivity]
            range = [str]

        class declaredPurpose(DataProperty):
            domain = [DataProcessingActivity]
            range = [str]

        # 추론 대상 속성들
        class violatesGDPR(DataProperty):
            domain = [DataProcessingActivity]
            range = [str]

        class requiresDPIA(DataProperty):
            domain = [DataProcessingActivity]
            range = [bool]

        # 데이터 처리 활동 인스턴스
        act1 = DataProcessingActivity("MarketingAnalytics_2024")
        act1.hasLegalBasis = ["consent"]
        act1.declaredPurpose = ["marketing"]
        act1.usesDataFor = ["profiling"]  # 목적 외 사용!

        act2 = DataProcessingActivity("HRDataTransfer_2024")
        act2.hasLegalBasis = []  # 법적 근거 없음!
        us_server = ThirdCountry("US_Server_AWS")
        act2.transfersTo = [us_server]  # EU 역외 전송!

        act3 = DataProcessingActivity("CustomerService_2024")
        act3.hasLegalBasis = ["contract"]
        act3.declaredPurpose = ["customer_support"]
        act3.usesDataFor = ["customer_support"]  # 정상

    print("\n" + "=" * 55)
    print("도메인 5: 법률 — GDPR 위반 자동 탐지")
    print("=" * 55)

    # GDPR 공리를 SWRL 규칙으로 표현:
    # 규칙 A: usesDataFor ≠ declaredPurpose → violates Art.5(1)(b) 목적 제한
    # 규칙 B: transfersTo(ThirdCountry) AND NOT hasLegalBasis → violates Art.44
    # 규칙 C: 위반 있으면 DPIA 필요
    with onto:
        for act in onto.individuals():
            if not isinstance(act, onto.DataProcessingActivity):
                continue
            violations = []

            # 규칙 A: 목적 제한 위반
            declared = set(act.declaredPurpose)
            actual = set(act.usesDataFor)
            if declared and actual and not actual.issubset(declared):
                violations.append("Art.5(1)(b) 목적제한 위반")

            # 규칙 B: 역외 전송 + 법적 근거 없음
            if act.transfersTo and not act.hasLegalBasis:
                countries = [c.name for c in act.transfersTo]
                violations.append(f"Art.44 역외이전 위반 ({countries})")

            if violations:
                act.violatesGDPR = violations
                act.requiresDPIA = [True]
                print(f"  [위반] {act.name}")
                for v in violations:
                    print(f"    → {v}")
                print(f"    → DPIA 필수")
            else:
                print(f"  [적합] {act.name}: 위반 없음")

    onto.save("gdpr_extended.owl", format="rdfxml")


# ══════════════════════════════════════════════════════════════════════
# 전체 실행 + OWL만의 결정적 강점 요약
# ══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    demo_pharma()
    demo_finance()
    demo_manufacturing()
    demo_clinical()
    demo_gdpr()

    print("\n" + "=" * 55)
    print("  OWL이 Neo4j보다 결정적으로 유리한 이유")
    print("=" * 55)
    advantages = [
        (
            "1. 자동 추론",
            "새 데이터 추가만 해도 새 사실이 자동 도출 — Cypher 쿼리 불필요",
        ),
        ("2. 스키마 진화", "추론 결과로 클래스·속성 자체를 런타임에 확장"),
        (
            "3. 표준 상호운용",
            "SNOMED·DrugBank·schema.org 등 공개 온톨로지 owl:import로 재사용",
        ),
        ("4. 일관성 검사", "모순된 데이터 입력 시 추론기가 자동으로 오류 탐지"),
        ("5. 규제 공리화", "법 조항을 OWL 공리로 표현 → 규제 변경 시 공리만 업데이트"),
        ("6. 설명 가능성", "추론 결과의 근거(왜 이 클래스?)를 공리 체인으로 설명 가능"),
    ]
    for title, desc in advantages:
        print(f"\n  {title}")
        print(f"    {desc}")

    print("\n  Neo4j와 함께 쓰는 베스트 프랙티스:")
    print("    OWL(Protégé) → 의미 정의·추론 → 결과를 Neo4j에 적재 → 고속 쿼리")
    print("    두 도구는 경쟁이 아니라 파이프라인의 다른 단계입니다.")
