"""Hybrid retriever using Elasticsearch RRF (Reciprocal Rank Fusion).

Combines BM25 text search with dense vector kNN search.
Uses ES 8.14+ RRF support with rank_constant=60.
"""

import os

from dotenv import load_dotenv
from elasticsearch import Elasticsearch

from ingest.embedding import embed_query

load_dotenv()

INDEX_NAME = "wiki-hybrid"


def get_es_client() -> Elasticsearch:
    return Elasticsearch(
        os.getenv("ELASTIC_ENDPOINT"),
        api_key=os.getenv("ELASTIC_API_KEY"),
        request_timeout=30,
    )


def search(query: str, top_k: int = 10, candidate_size: int = 50) -> list[dict]:
    """RRF hybrid search combining BM25 + kNN.

    Args:
        query: Search query string.
        top_k: Number of results to return.
        candidate_size: Number of kNN candidates before RRF fusion.

    Returns:
        list[dict], each dict has keys: "id", "text", "score", "method".
        "method" should be "Hybrid (RRF)".

    Hints:
        - Use embed_query(query) to get the query embedding vector
        - Use get_es_client() and es.search() with "retriever" parameter
        - RRF retriever combines "standard" (BM25 match) + "knn" retrievers
        - kNN field: "embedding", rank_constant: 60
        - num_candidates = candidate_size * 2
    """
    # 1. 검색 쿼리를 벡터로 변환
    query_vector = embed_query(query)

    # 2. Elasticsearch 클라이언트 생성
    es = get_es_client()

    # 3. RRF 리트리버를 사용한 검색 요청
    # standard(텍스트)와 knn(벡터) 검색을 결합하며, rank_constant는 60을 사용한다.
    response = es.search(
        index=INDEX_NAME, # "wiki-hybrid"
        retriever={
            "rrf": {
                "retrievers": [
                    {
                        "standard": {
                            "query": {"match": {"text": query}}
                        }
                    },
                    {
                        "knn": {
                            "field": "embedding", # kNN 필드 지정
                            "query_vector": query_vector,
                            "k": top_k,
                            "num_candidates": candidate_size * 2 # 힌트 적용
                        }
                    }
                ],
                "rank_constant": 60 # RRF 순위 상수
            }
        },
        size=top_k
    )

    # 4. 명세된 형식에 맞춰 결과 반환
    results = []
    for hit in response["hits"]["hits"]:
        results.append({
            "id": hit["_id"],
            "text": hit["_source"]["text"],
            "score": hit["_score"], # RRF 통합 점수
            "method": "Hybrid (RRF)" # 검색 방식
        })

    return results
