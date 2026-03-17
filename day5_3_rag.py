from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_classic.chains import create_retrieval_chain
from langchain_core.documents import Document

# 1. PDF 로드
print("=== PDF 로드 중... ===")
loader = PyPDFLoader("d:/ontology/안전관리실무_편집본.pdf")
pages = loader.load()
print(f"PDF 페이지 수: {len(pages)}")

# 2. 청킹
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
docs = text_splitter.split_documents(pages)
print(f"청크 수: {len(docs)}")

# 3. 제조 온톨로지 지식도 문서로 추가
from owlready2 import *
onto = get_ontology("d:/ontology/day5.owl").load()

ontology_docs = []
for b in onto.부품.instances():
    content = f"부품명: {b.name}"
    if b.무게: content += f", 무게: {b.무게[0]}kg"
    if b.불량율: content += f", 불량율: {b.불량율[0]*100:.1f}%"
    if onto.고위험부품 in b.is_a: content += ", 분류: 고위험부품 (점검필요)"
    if onto.핵심부품 in b.is_a: content += ", 분류: 핵심부품"
    ontology_docs.append(Document(page_content=content, metadata={"source": "ontology"}))

for 제품 in onto.제품.instances():
    부품목록 = [b.name for b in 제품.포함한다]
    if 부품목록:
        content = f"제품명: {제품.name}, 구성부품: {', '.join(부품목록)}"
        ontology_docs.append(Document(page_content=content, metadata={"source": "ontology"}))

print(f"온톨로지 문서 수: {len(ontology_docs)}")

# 4. PDF + 온톨로지 합쳐서 벡터 저장소 생성
all_docs = docs + ontology_docs
embeddings = OllamaEmbeddings(model="nomic-embed-text")
print("\n=== 벡터 저장소 생성 중... (시간이 걸려요) ===")
vectorstore = FAISS.from_documents(all_docs, embeddings)
print("벡터 저장소 생성 완료!")

# 5. RAG 체인 구성
llm = ChatOllama(model="llama3", temperature=0)
prompt = ChatPromptTemplate.from_template("""
아래 문맥을 바탕으로 질문에 반드시 한국어로 답해줘.
PDF 문서와 제조 온톨로지 정보를 모두 활용해줘.

<context>{context}</context>

질문: {input}
""")
chain = create_retrieval_chain(
    vectorstore.as_retriever(search_kwargs={"k": 5}),
    create_stuff_documents_chain(llm, prompt)
)

# 6. 질문
print("\n=== PDF + 온톨로지 통합 RAG 질의 ===\n")
questions = [
    "안전 관리에서 가장 중요한 점검 항목은?",
    "고위험부품은 어떤 것이 있어?",
    "산업용펌프의 구성 부품을 알려줘",
]
for q in questions:
    print(f"질문: {q}")
    result = chain.invoke({"input": q})
    print(f"답변: {result['answer']}")
    print("-" * 40)