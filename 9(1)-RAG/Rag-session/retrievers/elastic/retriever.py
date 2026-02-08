"""BM25 retriever using Elasticsearch."""

import os

from dotenv import load_dotenv
from elasticsearch import Elasticsearch

load_dotenv()

INDEX_NAME = "wiki-bm25"


def get_es_client() -> Elasticsearch:
    return Elasticsearch(
        os.getenv("ELASTIC_ENDPOINT"),
        api_key=os.getenv("ELASTIC_API_KEY"),
        request_timeout=30,
    )


def search(query: str, top_k: int = 10) -> list[dict]:
    """BM25 match search.

    Args:
        query: Search query string.
        top_k: Number of results to return.

    Returns:
        list[dict], each dict has keys: "id", "text", "score", "method".
        "method" should be "BM25".

    Hints:
        - Use get_es_client() and es.search()
        - Index name: INDEX_NAME
        - Use "match" query on "text" field
    """
    # 1. ES 클라이언트 생성
    es = get_es_client()

    # 2. 'text' 필드에 대한 match 쿼리 실행
    # size 파라미터로 반환할 결과 개수(top_k)를 지정한다.
    response = es.search(
        index=INDEX_NAME,
        query={"match": {"text": query}},
        size=top_k
    )

    # 3. 검색 결과를 명세된 dict 형식으로 변환
    results = []
    for hit in response["hits"]["hits"]:
        results.append({
            "id": hit["_id"], # 문서 고유 ID
            "text": hit["_source"]["text"], # 검색된 텍스트 본문
            "score": hit["_score"], # BM25 유사도 점수
            "method": "BM25"  # 검색 방법
        })

    return results
