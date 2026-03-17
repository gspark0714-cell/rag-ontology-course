from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from neo4j import GraphDatabase
import json

# LLM 설정
llm = ChatOllama(model="llama3", temperature=0)

# Neo4j 연결
driver = GraphDatabase.driver(
    "neo4j://127.0.0.1:7687",
    auth=("neo4j", "password123")
)

# LLM에게 관계 추출 요청하는 프롬프트
prompt = ChatPromptTemplate.from_template("""
아래 텍스트에서 제품/부품 간의 포함 관계를 추출해줘.
반드시 아래 JSON 형식으로만 답해줘. 다른 말은 하지 마.

텍스트: {text}

출력 형식:
[
  {{"부모": "부모이름", "자식": "자식이름"}},
  {{"부모": "부모이름", "자식": "자식이름"}}
]
""")

# 분석할 텍스트
text = """
컨베이어 시스템은 구동모터, 벨트, 롤러로 구성된다.
구동모터는 인버터와 감속기를 포함한다.
벨트는 텐셔너와 가이드롤러로 이루어진다.
"""

# LLM으로 관계 추출
print("--- LLM이 텍스트 분석 중... ---")
chain = prompt | llm
response = chain.invoke({"text": text})
print(f"LLM 추출 결과:\n{response.content}")

# JSON 파싱
try:
    # 백틱 제거 후 파싱
    content = response.content.strip()
    content = content.replace("```json", "").replace("```", "").strip()
    relations = json.loads(content)

    # Neo4j에 자동 입력
    with driver.session() as session:
        for rel in relations:
            session.run("""
                MERGE (parent:부품 {name: $부모})
                MERGE (child:부품 {name: $자식})
                MERGE (parent)-[:포함]->(child)
            """, 부모=rel['부모'], 자식=rel['자식'])
            print(f"Neo4j 입력 완료: {rel['부모']} → {rel['자식']}")

    print("--- 전체 입력 완료! ---")

except Exception as e:
    print(f"파싱 오류: {e}")
    print("LLM 응답을 확인하세요.")

driver.close()
