from langchain_neo4j import GraphCypherQAChain, Neo4jGraph
from langchain_ollama import ChatOllama

# Neo4j 연결
graph = Neo4jGraph(
    url="bolt://127.0.0.1:7687",
    username="neo4j",
    password="password123"
)

# 그래프 스키마 확인
print("--- 그래프 스키마 ---")
print(graph.schema)

# LLM 설정
llm = ChatOllama(model="llama3", temperature=0)

# 자연어 → Cypher → 결과 체인
chain = GraphCypherQAChain.from_llm(
    llm=llm,
    graph=graph,
    verbose=True,
    allow_dangerous_requests=True
)

# 질문하기
questions = [
    "산업용펌프에 포함된 부품이 뭐야?",
    "모터에 포함된 부품을 알려줘",
    "베어링은 어떤 제품에 사용돼?",
]

print("\n--- 자연어 질의 시작 ---")
for q in questions:
    print(f"\n질문: {q}")
    result = chain.invoke({"query": q})
    print(f"답변: {result['result']}")
    print("-" * 40)