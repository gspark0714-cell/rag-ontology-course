"""
# 현재 (Ollama)
from langchain_ollama import ChatOllama
llm = ChatOllama(model="llama3", temperature=0)

# 회사 자체 LLM으로 교체
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(
    base_url="http://회사서버주소:포트/v1",
    api_key="internal-key",
    model="모델명"
)


# 상단에 한 줄만 바꾸면 전환 가능하도록
USE_COMPANY_LLM = True  # False로 바꾸면 Ollama로 즉시 전환

if USE_COMPANY_LLM:
    from langchain_openai import ChatOpenAI
    llm = ChatOpenAI(base_url="http://서버:포트/v1", api_key="키", model="모델명")
else:
    from langchain_ollama import ChatOllama
    llm = ChatOllama(model="llama3", temperature=0)


"""

from langchain_ollama import ChatOllama
llm = ChatOllama(model="llama3", temperature=0)
