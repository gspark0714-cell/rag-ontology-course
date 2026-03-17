from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_classic.chains import create_retrieval_chain
from langchain_core.documents import Document
from owlready2 import *
from neo4j import GraphDatabase

print("=" * 60)
print("5일차 최종 통합 시스템")
print("Neo4j + OWL + PDF RAG")
print("=" * 60)

# 1. Neo4j 연결
driver = GraphDatabase.driver(
    "bolt://127.0.0.1:7687",
    auth=("neo4j", "password123")
)

# 2. OWL 로드
onto = get_ontology("d:/ontology/day5.owl").load()

# 3. LLM 설정
llm = ChatOllama(model="llama3", temperature=0)
embeddings = OllamaEmbeddings(model="nomic-embed-text")

# 4. Neo4j 그래프 검색 함수
def search_graph(question_type, value):
    with driver.session() as session:
        if question_type == "부품구성":
            result = session.run("""
                MATCH (a {name: $name})-[:포함]->(b)
                RETURN b.name AS 부품, b.불량율 AS 불량율
            """, name=value)
            return [(r['부품'], r['불량율']) for r in result]

        elif question_type == "불량추적":
            result = session.run("""
                MATCH (a)-[:포함*]->(b {name: $name})
                RETURN a.name AS 상위
            """, name=value)
            return [r['상위'] for r in result]

        elif question_type == "고위험":
            result = session.run("""
                MATCH (b:부품)
                WHERE b.불량율 > 0.03
                RETURN b.name AS 부품, b.불량율 AS 불량율
            """)
            return [(r['부품'], r['불량율']) for r in result]

    return []

# 5. OWL 추론 함수
def owl_reasoning(query_type):
    if query_type == "고위험":
        return [b.name for b in onto.고위험부품.instances()]
    elif query_type == "핵심":
        return [b.name for b in onto.핵심부품.instances()]
    return []

# 6. PDF + 온톨로지 벡터 저장소
print("\n벡터 저장소 구축 중...")
loader = PyPDFLoader("d:/ontology/안전관리실무_편집본.pdf")
pdf_docs = RecursiveCharacterTextSplitter(
    chunk_size=500, chunk_overlap=50
).split_documents(loader.load())

onto_docs = []
for b in onto.부품.instances():
    content = f"부품: {b.name}"
    if b.무게: content += f", 무게: {b.무게[0]}kg"
    if b.불량율: content += f", 불량율: {b.불량율[0]*100:.1f}%"
    if onto.고위험부품 in b.is_a: content += ", 고위험부품"
    if onto.핵심부품 in b.is_a: content += ", 핵심부품"
    onto_docs.append(Document(page_content=content))

vectorstore = FAISS.from_documents(pdf_docs + onto_docs, embeddings)
print("완료!")

# 7. 통합 질의 함수
def integrated_query(question):
    print(f"\n{'='*60}")
    print(f"질문: {question}")
    print(f"{'='*60}")

    # Neo4j 검색
    graph_info = ""
    if "구성" in question or "부품" in question:
        for 제품 in ["산업용펌프", "압력펌프"]:
            결과 = search_graph("부품구성", 제품)
            if 결과:
                graph_info += f"\n[그래프] {제품} 구성부품: "
                graph_info += ", ".join([f"{b}(불량율:{r*100:.1f}%)" if r else b for b, r in 결과])

    if "고위험" in question or "위험" in question or "점검" in question:
        결과 = search_graph("고위험", None)
        if 결과:
            graph_info += f"\n[그래프] 고위험부품: "
            graph_info += ", ".join([f"{b}(불량율:{r*100:.1f}%)" for b, r in 결과])

    if "영향" in question or "추적" in question:
        결과 = search_graph("불량추적", "베어링")
        if 결과:
            graph_info += f"\n[그래프] 베어링 불량 영향: {', '.join(결과)}"

    # OWL 추론
    owl_info = ""
    고위험 = owl_reasoning("고위험")
    핵심 = owl_reasoning("핵심")
    if 고위험: owl_info += f"\n[OWL] 고위험부품: {', '.join(고위험)}"
    if 핵심: owl_info += f"\n[OWL] 핵심부품: {', '.join(핵심)}"

    # RAG 검색
    rag_results = vectorstore.similarity_search(question, k=3)
    rag_info = "\n".join([d.page_content for d in rag_results])

    # 최종 통합 답변
    prompt = ChatPromptTemplate.from_template("""
아래 세 가지 소스의 정보를 종합해서 반드시 한국어로 답해줘.

[그래프 DB 정보 (Neo4j)]:
{graph_info}

[온톨로지 추론 정보 (OWL)]:
{owl_info}

[문서 검색 정보 (RAG)]:
{rag_info}

질문: {question}
""")
    chain = prompt | llm
    result = chain.invoke({
        "graph_info": graph_info if graph_info else "해당 없음",
        "owl_info": owl_info if owl_info else "해당 없음",
        "rag_info": rag_info,
        "question": question
    })

    if graph_info: print(graph_info)
    if owl_info: print(owl_info)
    print(f"\n[최종 답변]: {result.content}")

# 8. 질문하기
integrated_query("산업용펌프의 구성 부품과 불량율을 알려줘")
integrated_query("고위험부품은 무엇이고 어떻게 관리해야 해?")
integrated_query("베어링 불량이 발생하면 어떤 제품에 영향을 줘?")
integrated_query("안전 관리에서 가장 중요한 점검 항목은?")

driver.close()
print("\n=== 5일차 최종 시스템 완성! ===")