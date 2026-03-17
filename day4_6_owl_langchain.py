from owlready2 import *
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

# 1. OWL 파일 로드
onto = get_ontology("d:/ontology/manufacturing_swrl.owl").load()

# 2. LLM 설정
llm = ChatOllama(model="llama3", temperature=0)

# 3. 온톨로지에서 정보 추출 함수
def get_ontology_context():
    context = []

    # 제품-부품 관계
    for 제품 in onto.제품.instances():
        부품목록 = [b.name for b in 제품.포함한다]
        if 부품목록:
            context.append(f"{제품.name}은 {', '.join(부품목록)}으로 구성된다.")

    # 부품 정보
    for b in onto.부품.instances():
        info = f"{b.name}의 무게는 {b.무게[0]}kg이다." if b.무게 else ""
        if b.불량율:
            info += f" 불량율은 {b.불량율[0]*100:.1f}%이다."
        if onto.고위험부품 in b.is_a:
            info += f" 고위험부품으로 분류되어 점검이 필요하다."
        if info:
            context.append(info)

    # 공정 정보
    for p in onto.공정.instances():
        설비목록 = [s.name for s in p.사용한다]
        if p.작업시간 and 설비목록:
            context.append(f"{p.name}은 작업시간이 {p.작업시간[0]}분이고 {', '.join(설비목록)}을 사용한다.")

    return "\n".join(context)

# 4. RAG 체인 구성
prompt = ChatPromptTemplate.from_template("""
아래는 제조 온톨로지 지식베이스 정보입니다:

{context}

위 정보를 바탕으로 질문에 반드시 한국어로 답해줘.
모르는 내용은 "정보가 없습니다"라고 답해줘.

질문: {question}
""")

chain = prompt | llm

# 5. 질문하기
context = get_ontology_context()
print("=== 온톨로지 지식베이스 내용 ===")
print(context)
print("\n=== 자연어 질의 시작 ===\n")

questions = [
    "산업용펌프는 어떤 부품으로 구성되어 있어?",
    "점검이 필요한 부품은 뭐야?",
    "가장 무거운 부품은 뭐야?",
    "가공공정1에서 사용하는 설비는?",
    "베어링에 문제가 생기면 어떤 제품에 영향을 줘?",
]

for q in questions:
    print(f"질문: {q}")
    result = chain.invoke({"context": context, "question": q})
    print(f"답변: {result.content}")
    print("-" * 40)