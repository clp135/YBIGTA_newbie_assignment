"""Vector retriever using Pinecone (cosine similarity)."""

import os

from dotenv import load_dotenv
from pinecone import Pinecone

from ingest.embedding import embed_query

load_dotenv()


def search(query: str, top_k: int = 10) -> list[dict]:
    """Vector cosine similarity search.

    Args:
        query: Search query string.
        top_k: Number of results to return.

    Returns:
        list[dict], each dict has keys: "id", "text", "score", "method".
        "method" should be "Vector".

    Hints:
        - Use embed_query(query) to get the query embedding vector
        - Connect: Pinecone(api_key=...) → pc.Index(index_name)
        - Use index.query(vector=..., top_k=..., include_metadata=True)
        - Text is in match["metadata"]["text"]
    """
    # 1. 질문(query)을 임베딩 벡터로 변환
    query_vector = embed_query(query)

    # 2. Pinecone 클라이언트 연결 및 인덱스 설정
    api_key = os.getenv("PINECONE_API_KEY")
    index_name = os.getenv("PINECONE_INDEX", "ragsession")
    pc = Pinecone(api_key=api_key)
    index = pc.Index(index_name)

    # 3. 벡터 검색 수행 (유사도 점수 및 메타데이터 포함)
    # include_metadata=True를 설정해야 'text' 필드를 가져올 수 있다.
    response = index.query(
        vector=query_vector,
        top_k=top_k,
        include_metadata=True
    )

    # 4. 결과를 명세된 리스트(dict) 형식으로 변환
    results = []
    for match in response["matches"]:
        results.append({
            "id": match["id"],
            "text": match["metadata"].get("text", ""), # 메타데이터에서 텍스트 추출
            "score": match["score"], # 유사도 점수
            "method": "Vector" # 검색 방식
        })

    return results
