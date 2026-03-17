from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_classic.chains import create_retrieval_chain

loader = PyPDFLoader("d:/ontology/안전관리실무_편집본.pdf")
pages = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
docs = text_splitter.split_documents(pages)

embeddings = OllamaEmbeddings(model="nomic-embed-text")
vectorstore = FAISS.from_documents(docs, embeddings)

llm = ChatOllama(model="llama3")
prompt = ChatPromptTemplate.from_template("""
아래 문맥을 바탕으로 반드시 한국어로 질문에 답해줘.
<context>{context}</context>
질문: {input}
""")
document_chain = create_stuff_documents_chain(llm, prompt)
retrieval_chain = create_retrieval_chain(vectorstore.as_retriever(), document_chain)

print("--- PDF 내용 기반 질문 시작 ---")
result = retrieval_chain.invoke({"input": "이 문서의 핵심 내용을 요약해줘."})
print(f"답변: {result['answer']}")