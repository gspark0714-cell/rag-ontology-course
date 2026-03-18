# ================================================================
# chunking_strategy.py — 제조 문서 청킹 전략 비교 실습
# ================================================================
# 제조 비정형 문서(매뉴얼, 리포트)는 문서 구조가 다양해서
# 어떻게 자르느냐에 따라 RAG 검색 품질이 크게 달라집니다.
#
# 이 실습에서 비교할 전략:
#   전략 1: 고정 크기 청킹 (가장 단순)
#   전략 2: 문단 기반 청킹 (구조 인식)
#   전략 3: 섹션 기반 청킹 (제목 인식)
#   전략 4: 하이브리드 청킹 (전략 2+3 결합, 최고 성능)
# ================================================================

from config import get_llm, get_embeddings

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
    CharacterTextSplitter,
)
# RecursiveCharacterTextSplitter: 문단→문장→단어 순으로 재귀적으로 분할
# CharacterTextSplitter: 특정 구분자 기준으로 분할

import re
# re: 정규표현식 모듈 — 패턴으로 텍스트 찾기/분리에 사용

llm        = get_llm()
embeddings = get_embeddings()

# ─── 문서 불러오기 ───────────────────────────────────────────────
def load_txt(path):
    """텍스트 파일을 읽어서 Document 객체로 반환"""
    with open(path, encoding="utf-8") as f:
        content = f.read()
    return Document(
        page_content=content,
        metadata={"source": path}
        # metadata: 이 문서의 출처 정보 저장
        # 나중에 검색 결과에서 "어느 파일에서 왔는지" 확인 가능
    )

# 3개 문서 모두 불러오기
docs_raw = [
    load_txt("sample_docs/설비점검매뉴얼.txt"),
    load_txt("sample_docs/품질검사리포트_2024년3월.txt"),
    load_txt("sample_docs/작업표준서_펌프조립.txt"),
]

print("=" * 60)
print("  제조 문서 청킹 전략 비교 실습")
print("=" * 60)
print(f"\n  로드된 문서: {len(docs_raw)}개")
for d in docs_raw:
    print(f"  - {d.metadata['source']} ({len(d.page_content)}자)")

# ================================================================
# 전략 1: 고정 크기 청킹
# ================================================================
# 가장 단순한 방식 — 글자 수만 세서 자름
# 장점: 구현 간단, 청크 크기 예측 가능
# 단점: 문장/문단 중간에서 잘릴 수 있음
#       "베어링 온도는 70℃를 초과하면..." 이 잘리면 의미 손실
# ================================================================
print("\n" + "─" * 60)
print("  [전략 1] 고정 크기 청킹")
print("─" * 60)

fixed_splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,     # 300자마다 자름
    chunk_overlap=30,   # 앞뒤 30자 겹침
    length_function=len,
)
fixed_chunks = fixed_splitter.split_documents(docs_raw)

print(f"  총 청크 수: {len(fixed_chunks)}개")
print(f"  청크 크기 분포:")
sizes = [len(c.page_content) for c in fixed_chunks]
print(f"    최소: {min(sizes)}자")
print(f"    최대: {max(sizes)}자")
print(f"    평균: {sum(sizes)//len(sizes)}자")
print(f"\n  샘플 청크 (3번째):")
print(f"  {'─'*40}")
print(f"  {fixed_chunks[2].page_content[:200]}")
print(f"  {'─'*40}")
print(f"  ⚠ 문장 중간에서 잘렸나요? 확인해보세요!")


# ================================================================
# 전략 2: 문단 기반 청킹
# ================================================================
# 빈 줄(\n\n)을 기준으로 자름 → 문단 단위로 분리
# 장점: 의미 단위(문단)가 유지됨
# 단점: 문단 길이가 들쭉날쭉하면 청크 크기도 불균일
# ================================================================
print("\n" + "─" * 60)
print("  [전략 2] 문단 기반 청킹 (\\n\\n 기준)")
print("─" * 60)

paragraph_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separators=[
        "\n\n",    # 1순위: 빈 줄 (문단 구분)
        "\n",      # 2순위: 줄바꿈 (문장 구분)
        "。",      # 3순위: 마침표
        " ",       # 4순위: 공백
        "",        # 5순위: 글자 단위 (최후 수단)
    ]
    # separators 리스트 순서대로 시도하다가
    # chunk_size 초과하면 다음 구분자로 넘어감
)
para_chunks = paragraph_splitter.split_documents(docs_raw)

print(f"  총 청크 수: {len(para_chunks)}개")
print(f"\n  샘플 청크 비교 (문단이 잘 유지되는지 확인):")
for i, chunk in enumerate(para_chunks[3:6], 1):
    print(f"\n  [청크 {i}] ({len(chunk.page_content)}자)")
    print(f"  {chunk.page_content[:180]}")
    print(f"  {'.'*40}")


# ================================================================
# 전략 3: 섹션 기반 청킹 (커스텀)
# ================================================================
# 제조 문서는 보통 "제1장", "1.1", "STEP 1" 같은
# 섹션 구조를 가지고 있음
# → 이 구조를 인식해서 자르면 의미가 가장 잘 보존됨
#
# 장점: 섹션 단위로 완결된 내용이 한 청크에 담김
# 단점: 커스텀 코드 필요, 문서마다 패턴이 다름
# ================================================================
print("\n" + "─" * 60)
print("  [전략 3] 섹션 기반 청킹 (제목 패턴 인식)")
print("─" * 60)

def section_based_chunking(documents, max_chunk_size=800):
    """
    섹션 제목을 인식해서 문서를 섹션 단위로 분리하는 함수
    
    인식하는 패턴:
    - "제1장", "제2장" 등 장 구분
    - "1.1", "2.3" 등 소제목
    - "STEP 1", "STEP 2" 등 작업 단계
    - "━━━" 등 구분선
    """
    
    # 섹션 시작을 나타내는 패턴들
    section_patterns = [
        r'^제\d+장',           # 제1장, 제2장
        r'^\d+\.\s',           # 1. 작업 준비
        r'^\d+\.\d+\s',        # 1.1 베어링 점검
        r'^STEP\s+\d+',        # STEP 1, STEP 2
        r'^━+',                # ━━━ (구분선)
        r'^\[고장유형',         # [고장유형 1]
        r'^\d+\.\s+\S+.*:',    # 번호 목록
    ]
    
    # 패턴들을 하나의 정규식으로 합치기
    combined_pattern = '|'.join(f'({p})' for p in section_patterns)
    
    all_chunks = []
    
    for doc in documents:
        text   = doc.page_content
        source = doc.metadata.get('source', 'unknown')
        lines  = text.split('\n')
        
        current_section_title = "시작"
        current_content       = []
        
        for line in lines:
            # 이 줄이 섹션 제목 패턴에 맞는지 확인
            is_section_start = bool(re.match(combined_pattern, line.strip()))
            
            if is_section_start and current_content:
                # 새 섹션 시작 → 현재까지 모은 내용을 청크로 저장
                content_text = '\n'.join(current_content).strip()
                
                if len(content_text) > 50:  # 너무 짧은 청크 제외
                    if len(content_text) <= max_chunk_size:
                        # 크기 OK → 그대로 청크로 저장
                        all_chunks.append(Document(
                            page_content=content_text,
                            metadata={
                                "source":  source,
                                "section": current_section_title,
                                "strategy": "섹션기반"
                            }
                        ))
                    else:
                        # 너무 크면 → RecursiveCharacterTextSplitter로 추가 분할
                        sub_splitter = RecursiveCharacterTextSplitter(
                            chunk_size=max_chunk_size,
                            chunk_overlap=80
                        )
                        sub_chunks = sub_splitter.split_text(content_text)
                        for j, sc in enumerate(sub_chunks):
                            all_chunks.append(Document(
                                page_content=sc,
                                metadata={
                                    "source":  source,
                                    "section": f"{current_section_title} (파트{j+1})",
                                    "strategy": "섹션기반+분할"
                                }
                            ))
                
                # 새 섹션 시작
                current_section_title = line.strip()
                current_content       = [line]
            else:
                current_content.append(line)
        
        # 마지막 섹션 저장
        if current_content:
            content_text = '\n'.join(current_content).strip()
            if len(content_text) > 50:
                all_chunks.append(Document(
                    page_content=content_text,
                    metadata={
                        "source":  source,
                        "section": current_section_title,
                        "strategy": "섹션기반"
                    }
                ))
    
    return all_chunks

section_chunks = section_based_chunking(docs_raw)

print(f"  총 청크 수: {len(section_chunks)}개")
print(f"\n  섹션별 청크 목록 (처음 8개):")
for i, chunk in enumerate(section_chunks[:8], 1):
    print(f"  [{i}] 섹션: '{chunk.metadata.get('section', '?')[:30]}'")
    print(f"       크기: {len(chunk.page_content)}자")
    print(f"       내용: {chunk.page_content[:80].strip()}...")
    print()


# ================================================================
# 전략 4: 하이브리드 청킹 (메타데이터 강화)
# ================================================================
# 전략 2(문단기반) + 전략 3(섹션기반)의 장점을 합침
# + 각 청크에 풍부한 메타데이터를 추가
#
# 핵심 아이디어:
# - 문서 유형을 자동으로 감지 (매뉴얼 vs 리포트 vs SOP)
# - 청크에 문서유형, 섹션, 키워드 등 메타데이터 추가
# - 검색 시 메타데이터 필터링으로 정확도 향상
# ================================================================
print("\n" + "─" * 60)
print("  [전략 4] 하이브리드 청킹 (메타데이터 강화)")
print("─" * 60)

def detect_doc_type(text):
    """
    텍스트 내용을 보고 문서 유형을 자동 감지하는 함수
    """
    text_lower = text.lower()
    if any(kw in text for kw in ["매뉴얼", "점검 절차", "점검 항목", "고장 대응"]):
        return "매뉴얼"
    elif any(kw in text for kw in ["리포트", "불량률", "생산량", "개선활동"]):
        return "품질리포트"
    elif any(kw in text for kw in ["SOP", "작업표준", "작업 순서", "STEP"]):
        return "작업표준서"
    else:
        return "기타"

def extract_keywords(text):
    """
    제조 관련 핵심 키워드를 추출하는 함수
    실제로는 NLP 라이브러리를 쓰지만 여기서는 규칙 기반으로 단순화
    """
    # 제조 관련 주요 키워드 목록
    manufacturing_keywords = [
        "베어링", "임펠러", "케이싱", "모터", "펌프", "컨베이어",
        "불량", "불량률", "점검", "교체", "온도", "진동", "압력",
        "토크", "볼트", "씰", "오일", "윤활", "가공", "조립",
        "검사", "기준", "허용값", "정격", "과열", "누수"
    ]
    found = [kw for kw in manufacturing_keywords if kw in text]
    return found[:5]  # 최대 5개만 반환

def hybrid_chunking(documents):
    """
    하이브리드 청킹: 섹션 분리 + 문단 분리 + 메타데이터 강화
    """
    # 1단계: 섹션 기반으로 1차 분리
    section_chunks_temp = section_based_chunking(documents, max_chunk_size=600)
    
    # 2단계: 각 청크에 메타데이터 강화
    enriched_chunks = []
    
    for chunk in section_chunks_temp:
        text     = chunk.page_content
        source   = chunk.metadata.get('source', '')
        section  = chunk.metadata.get('section', '')
        doc_type = detect_doc_type(text)
        keywords = extract_keywords(text)
        
        # 수치 데이터가 있는 청크 감지
        # (온도, 압력, 불량률 같은 숫자+단위 패턴)
        has_numeric = bool(re.search(r'\d+[\.,]?\d*\s*(℃|mm|N·m|%|rpm|dB|MΩ)', text))
        
        enriched_chunks.append(Document(
            page_content=text,
            metadata={
                "source":      source,
                "section":     section,
                "doc_type":    doc_type,      # 문서 유형
                "keywords":    keywords,       # 핵심 키워드
                "has_numeric": has_numeric,    # 수치 데이터 포함 여부
                "char_count":  len(text),      # 청크 크기
                "strategy":    "하이브리드",
            }
        ))
    
    return enriched_chunks

hybrid_chunks = hybrid_chunking(docs_raw)

print(f"  총 청크 수: {len(hybrid_chunks)}개")
print(f"\n  문서 유형별 청크 분포:")
type_counts = {}
for chunk in hybrid_chunks:
    t = chunk.metadata.get('doc_type', '?')
    type_counts[t] = type_counts.get(t, 0) + 1
for doc_type, count in type_counts.items():
    print(f"    {doc_type}: {count}개")

print(f"\n  수치 데이터 포함 청크: "
      f"{sum(1 for c in hybrid_chunks if c.metadata.get('has_numeric'))}개")

print(f"\n  메타데이터 강화 샘플 (2개):")
for chunk in hybrid_chunks[2:4]:
    print(f"\n  {'─'*40}")
    print(f"  문서유형: {chunk.metadata['doc_type']}")
    print(f"  섹션:     {chunk.metadata['section'][:40]}")
    print(f"  키워드:   {chunk.metadata['keywords']}")
    print(f"  수치포함: {chunk.metadata['has_numeric']}")
    print(f"  내용:     {chunk.page_content[:120].strip()}...")


# ================================================================
# 전략별 성능 비교 테스트
# ================================================================
print("\n" + "─" * 60)
print("  [성능 비교] 전략별 검색 품질 테스트")
print("─" * 60)

strategies = [
    ("고정 크기",   fixed_chunks),
    ("문단 기반",   para_chunks),
    ("섹션 기반",   section_chunks),
    ("하이브리드",  hybrid_chunks),
]

test_queries = [
    "베어링 교체 주기는 얼마나 돼?",
    "케이싱 불량의 원인이 뭐야?",
    "임펠러 너트 조임 토크는?",
]

for query in test_queries:
    print(f"\n  질문: '{query}'")
    print(f"  {'─'*50}")
    
    for strategy_name, chunks in strategies:
        try:
            vs     = FAISS.from_documents(chunks, embeddings)
            result = vs.similarity_search(query, k=1)
            hit    = result[0].page_content[:100].replace('\n', ' ')
            section = result[0].metadata.get('section', '─')[:20]
            print(f"  [{strategy_name:8}] 섹션:{section:20} → {hit}...")
        except Exception as e:
            print(f"  [{strategy_name:8}] 오류: {e}")

print("\n" + "=" * 60)
print("  청킹 전략 비교 완료!")
print("=" * 60)
print("""
  📌 결론:
  ─────────────────────────────────────────────────────
  전략 1 (고정 크기)  → 간단하지만 문장이 잘릴 수 있음
  전략 2 (문단 기반)  → 문맥 유지, 일반 문서에 적합
  전략 3 (섹션 기반)  → 구조화된 문서에 강함
  전략 4 (하이브리드) → 메타데이터 활용으로 가장 정확
  ─────────────────────────────────────────────────────
  제조 문서는 대부분 구조화되어 있으므로
  전략 4 (하이브리드)를 권장합니다!
""")