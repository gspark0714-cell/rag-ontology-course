from langchain_neo4j import GraphCypherQAChain, Neo4jGraph
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_classic.chains import create_retrieval_chain

# 1. Neo4j 그래프 연결
graph = Neo4jGraph(
    url="bolt://127.0.0.1:7687",
    username="neo4j",
    password="password123"
)

# 2. LLM 설정
llm = ChatOllama(model="llama3", temperature=0)

# 3. 그래프 검색 체인
#1) 잘 모른다고 답이 나올 수도 있는 코드
# cypher_prompt = PromptTemplate(
#     input_variables=["schema", "question"],
#     template="""
# Neo4j 데이터베이스 스키마:
# {schema}

# 중요 규칙:
# - 노드를 찾을 때 라벨(제품, 부품)을 쓰지 마
# - name 속성으로만 검색해
# - 예시: MATCH (a {{name: '모터'}})-[:포함]->(b) RETURN b.name

# 질문: {question}
# Cypher 쿼리만 출력해. 설명 없이.
# """
# )

#2) 1)번이 잘 안됐을때 테스트 해 볼 코드
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

graph_chain = GraphCypherQAChain.from_llm(
    llm=llm,
    graph=graph,
    verbose=False,
    allow_dangerous_requests=True,
    cypher_prompt=cypher_prompt
)

# 4. 벡터 검색용 간단한 문서 준비
from langchain_core.documents import Document

documents = [
    Document(page_content="산업용펌프는 모터, 임펠러, 케이싱으로 구성된다. 고압 유체를 이송하는 장비이다."),
    Document(page_content="모터는 베어링과 샤프트를 포함한다. 전기 에너지를 기계 에너지로 변환한다."),
    Document(page_content="베어링은 회전축을 지지하는 부품이다. 마모가 심하면 진동과 소음이 발생한다."),
    Document(page_content="압력펌프는 피스톤, 모터, 밸브로 구성된다. 높은 압력이 필요한 곳에 사용한다."),
    Document(page_content="케이싱은 볼트와 개스킷으로 조립된다. 내부 유체가 누설되지 않도록 밀봉한다."),
]

embeddings = OllamaEmbeddings(model="nomic-embed-text")
vectorstore = FAISS.from_documents(documents, embeddings)

# 5. 문서 검색 체인
doc_prompt = ChatPromptTemplate.from_template("""
아래 문서 내용을 참고해서 반드시 한국어로 답해줘.
<context>{context}</context>
질문: {input}
""")
doc_chain = create_retrieval_chain(
    vectorstore.as_retriever(),
    create_stuff_documents_chain(llm, doc_prompt)
)

# 6. Graph RAG — 두 가지 검색 결합
def graph_rag(question):
    print(f"\n질문: {question}")
    print("-" * 40)

    # 그래프에서 구조 정보 검색
    graph_result = graph_chain.invoke({"query": question})
    print(f"그래프 검색 결과: {graph_result['result']}")

    # 문서에서 설명 정보 검색
    doc_result = doc_chain.invoke({"input": question})
    print(f"문서 검색 결과: {doc_result['answer']}")

    # 두 결과 합쳐서 최종 답변
    final_prompt = f"""
그래프 DB 검색 결과: {graph_result['result']}
문서 검색 결과: {doc_result['answer']}

위 두 가지 정보를 합쳐서 '{question}' 에 대해 한국어로 종합 답변해줘.
"""
    final = llm.invoke(final_prompt)
    print(f"\n최종 종합 답변: {final.content}")
    print("=" * 40)

# 7. 질문하기
graph_rag("모터에 포함된 부품과 그 역할을 알려줘")
graph_rag("산업용펌프의 구성 부품을 설명해줘")