from langchain_ollama import ChatOllama

# 1. 로컬에 설치된 Ollama 모델 연결
llm = ChatOllama(
    model="llama3",
    temperature=0, # 답변의 일관성을 위해 0으로 설정
)

# 2. 질문 던져보기
try:
    print("--- 로컬 LLM(Llama 3)에게 질문을 보냅니다 ---")
    question = "온톨로지와 RAG의 차이점을 짧게 설명해줘."
    response = llm.invoke(question)
    
    print(f"답변: {response.content}")
    print("--- 로컬 연결 성공! ---")
except Exception as e:
    print(f"에러 발생: {e}")