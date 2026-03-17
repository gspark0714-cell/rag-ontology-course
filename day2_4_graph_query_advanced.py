from langchain_neo4j import GraphCypherQAChain, Neo4jGraph
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate

# Neo4j 연결
graph = Neo4jGraph(
    url="bolt://127.0.0.1:7687",
    username="neo4j",
    password="password123"
)

# LLM 설정
llm = ChatOllama(model="llama3", temperature=0)

# LLM에게 스키마를 명확히 알려주는 프롬프트
cypher_prompt = PromptTemplate(
    input_variables=["schema", "question"],
    template="""
Neo4j 데이터베이스 스키마:
{schema}

중요 규칙:
- 노드를 찾을 때 라벨(제품, 부품)을 쓰지 마
- 반드시 이 형식으로만 써: MATCH (a {{name: '이름'}})-[:포함]->(b) RETURN b.name
- name 속성으로만 검색해

예시:
- "모터에 포함된 부품": MATCH (a {{name: '모터'}})-[:포함]->(b) RETURN b.name
- "산업용펌프의 부품": MATCH (a {{name: '산업용펌프'}})-[:포함]->(b) RETURN b.name
- "베어링이 사용된 곳": MATCH (a)-[:포함]->(b {{name: '베어링'}}) RETURN a.name

질문: {question}

Cypher 쿼리만 출력해. 설명 없이.
"""
)

# 자연어 → Cypher → 결과 체인
chain = GraphCypherQAChain.from_llm(
    llm=llm,
    graph=graph,
    verbose=True,
    allow_dangerous_requests=True,
    cypher_prompt=cypher_prompt
)

# 질문하기
questions = [
    "산업용펌프에 포함된 부품이 뭐야?",
    "모터에 포함된 부품을 알려줘",
    "베어링은 어떤 부품에 사용돼?",
]

print("\n--- 자연어 질의 시작 ---")
for q in questions:
    print(f"\n질문: {q}")
    result = chain.invoke({"query": q})
    print(f"답변: {result['result']}")
    print("-" * 40)