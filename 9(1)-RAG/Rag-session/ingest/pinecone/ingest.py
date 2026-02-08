"""Ingest embeddings into Pinecone vector index.

Batch upsert: 100 vectors per call.
Metadata: text truncated to 1000 chars (40KB limit).
"""

import json
import os
from pathlib import Path

import numpy as np
from dotenv import load_dotenv
from pinecone import Pinecone

load_dotenv()

# --- 경로 설정 ---
# 파일 위치: ingest/pinecone/ingest.py
# parent: pinecone/, parent.parent: ingest/, parent.parent.parent: project/
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

EMBEDDINGS_PATH = PROCESSED_DIR / "embeddings.npy"
IDS_PATH = PROCESSED_DIR / "embedding_ids.json"

# --- 설정값 ---
BATCH_SIZE = 100
TEXT_LIMIT = 1000


def ingest(progress_callback=None):
    """Batch upsert embeddings into Pinecone vector index.

    Args:
        progress_callback: Optional callback(current, total) for progress updates.

    Returns:
        int: Number of vectors upserted.

    Hints:
        - Load embeddings from PROCESSED_DIR / "embeddings.npy"
        - Load IDs from PROCESSED_DIR / "embedding_ids.json"
        - Load texts from RAW_DIR / "corpus.jsonl" for metadata
        - Connect: Pinecone(api_key=...) → pc.Index(index_name)
        - Upsert format: {"id": ..., "values": [...], "metadata": {"text": ...}}
        - Batch size: BATCH_SIZE (100), truncate text to TEXT_LIMIT (1000) chars
    """
    # TODO: Implement Pinecone upsert
    # 1. 임베딩 및 ID 로드
    if not EMBEDDINGS_PATH.exists() or not IDS_PATH.exists():
        raise FileNotFoundError("임베딩 파일이 존재하지 않는다. 먼저 embedding.py를 실행해야 한다.")
    
    embeddings = np.load(EMBEDDINGS_PATH)
    with open(IDS_PATH, "r", encoding="utf-8") as f:
        ids = json.load(f)

    # 2. 메타데이터용 텍스트 로드 (corpus.jsonl)
    texts = {}
    corpus_path = RAW_DIR / "corpus.jsonl"
    with open(corpus_path, "r", encoding="utf-8") as f:
        for line in f:
            doc = json.loads(line)
            # 메타데이터 크기 제한을 위해 텍스트 절단
            texts[str(doc["id"])] = doc["text"][:TEXT_LIMIT]

    # 3. Pinecone 연결 설정
    api_key = os.getenv("PINECONE_API_KEY")
    index_name = os.getenv("PINECONE_INDEX", "ragsession")
    pc = Pinecone(api_key=api_key)
    index = pc.Index(index_name)

    # 4. 배치 단위로 Upsert 수행
    total = len(ids)
    upserted_count = 0

    for i in range(0, total, BATCH_SIZE):
        batch_ids = ids[i : i + BATCH_SIZE]
        batch_vectors = []
        
        for j, doc_id in enumerate(batch_ids):
            idx = i + j
            vector_data = {
                "id": str(doc_id),
                "values": embeddings[idx].tolist(),
                "metadata": {"text": texts.get(str(doc_id), "")}
            }
            batch_vectors.append(vector_data)
        
        # Pinecone에 적재
        index.upsert(vectors=batch_vectors)
        
        upserted_count += len(batch_vectors)
        if progress_callback:
            progress_callback(upserted_count, total)

    return upserted_count


if __name__ == "__main__":
    ingest()
