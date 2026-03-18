# config.py — 모든 실습 파일에서 공통으로 불러쓰는 설정

def get_llm():
    """회사 LLM → Ollama 순서로 자동 선택"""
    try:
        from langchain_openai import ChatOpenAI
        llm = ChatOpenAI(
            base_url="https://gpt-hr.platform.haiqv.ai/v1",
            api_key="none",
            model="GPT-OSS-120B",
            temperature=0,
        )
        llm.invoke("test")
        print("✅ 회사 LLM 사용 중")
        return llm
    except:
        pass
    try:
        from langchain_ollama import ChatOllama
        llm = ChatOllama(model="llama3", temperature=0)
        llm.invoke("test")
        print("✅ Ollama llama3 사용 중")
        return llm
    except:
        raise Exception("❌ LLM 연결 실패 — 강사에게 문의하세요")

def get_embeddings():
    """회사 임베딩 → Ollama 순서로 자동 선택"""
    try:
        from langchain_openai import OpenAIEmbeddings
        emb = OpenAIEmbeddings(
            base_url="https://qwen-embed-hr.platform.haiqv.ai/v1",
            api_key="none",
            model="Qwen3-Embedding-4B",
            dimensions=2560,
        )
        emb.embed_query("test")
        print("✅ 회사 임베딩 사용 중")
        return emb
    except:
        pass
    try:
        from langchain_ollama import OllamaEmbeddings
        emb = OllamaEmbeddings(model="nomic-embed-text")
        emb.embed_query("test")
        print("✅ Ollama 임베딩 사용 중")
        return emb
    except:
        raise Exception("❌ 임베딩 연결 실패 — 강사에게 문의하세요")