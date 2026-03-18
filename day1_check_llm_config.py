# my_rag.py
from config import get_llm, get_embeddings          
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_classic.chains import create_retrieval_chain

# LLM, 임베딩 자동 선택
llm        = get_llm()
embeddings = get_embeddings()

# PDF 로드
loader = PyPDFLoader('안전관리실무_편집본.pdf')
pages  = loader.load()
print(f'총 페이지 수: {len(pages)}')

# 청킹
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
docs = text_splitter.split_documents(pages)
print(f'총 청크 수: {len(docs)}')
print(docs[0].page_content[:200])

# 벡터 저장소
vectorstore = FAISS.from_documents(docs, embeddings)

# 유사도 검색 테스트
results  = vectorstore.similarity_search('안전 관리', k=3)
results2 = vectorstore.similarity_search('연안사고 예방', k=3)

print("-" * 50)
for r in results:
    print(r.page_content[:100])
    print("=" * 50)

print("-" * 50)
for r in results2:
    print(r.page_content[:100])
    print("=" * 50)

# RAG 체인 구성
prompt = ChatPromptTemplate.from_template("""
아래 문맥을 바탕으로 반드시 한국어로 답해줘.
<context>{context}</context>
질문: {input}
""")
chain = create_retrieval_chain(
    vectorstore.as_retriever(search_kwargs={"k": 3}),
    create_stuff_documents_chain(llm, prompt)
)

# 질문
questions = [
    "안전 관리에서 가장 중요한 점검 항목은?",
    "연안사고를 예방하는 방법은?",
]
for q in questions:
    print(f"\n질문: {q}")
    result = chain.invoke({"input": q})
    print(f"답변: {result['answer']}")
