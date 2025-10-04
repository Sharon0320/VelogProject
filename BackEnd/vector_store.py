import os
import hashlib
from typing import List, Tuple, Optional

import numpy as np
import psycopg2
from psycopg2.extras import execute_values
from pgvector.psycopg2 import register_vector


EMBEDDING_DIM = 384  # all-MiniLM-L6-v2


def derive_user_id_from_cookie(cookie_value: str) -> str:
    if not cookie_value:
        return "anonymous"
    return hashlib.sha256(cookie_value.encode("utf-8")).hexdigest()[:16]


class VectorStore:
    def __init__(self) -> None:
        self.conn = None
        self._connect()
        self._ensure_schema()

    def _connect(self) -> None:
        try:
            self.conn = psycopg2.connect(
                host=os.getenv("PGHOST", "localhost"),
                port=int(os.getenv("PGPORT", "5432")),
                dbname=os.getenv("PGDATABASE", "velog"),
                user=os.getenv("PGUSER", "velog"),
                password=os.getenv("PGPASSWORD", "velog")
            )
            self.conn.autocommit = True
            print("✅ PostgreSQL 연결 성공")
        except Exception as e:
            print(f"❌ PostgreSQL 연결 실패: {e}")
            self.conn = None

    def _ensure_schema(self) -> None:
        if not self.conn:
            return
        try:
            with self.conn.cursor() as cur:
                cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
                print("✅ pgvector 확장 생성 완료")
                
                # 확장 생성 후 register_vector 호출
                register_vector(self.conn)
                print("✅ pgvector 타입 등록 완료")
                
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS user_embeddings (
                      id BIGSERIAL PRIMARY KEY,
                      user_id TEXT NOT NULL,
                      post_id TEXT,
                      content TEXT NOT NULL,
                      embedding VECTOR(%s) NOT NULL,
                      created_at TIMESTAMP DEFAULT NOW()
                    );
                    """,
                    (EMBEDDING_DIM,),
                )
                cur.execute(
                    "CREATE INDEX IF NOT EXISTS idx_user_embeddings_user_id ON user_embeddings(user_id);"
                )
                cur.execute(
                    "CREATE INDEX IF NOT EXISTS idx_user_embeddings_embedding ON user_embeddings USING ivfflat (embedding vector_cosine_ops);"
                )
                print("✅ 테이블 및 인덱스 생성 완료")
        except Exception as e:
            print(f"❌ 스키마 생성 실패: {e}")
            self.conn = None

    def available(self) -> bool:
        return self.conn is not None

    def upsert_documents(self, user_id: str, documents: List[Tuple[str, str, np.ndarray]]) -> None:
        if not self.conn or not documents:
            return
        with self.conn.cursor() as cur:
            execute_values(
                cur,
                """
                INSERT INTO user_embeddings (user_id, post_id, content, embedding)
                VALUES %s
                """,
                [(user_id, post_id, content, embedding.tolist()) for (post_id, content, embedding) in documents],
            )

    def similarity_search(self, user_id: str, query_embedding: np.ndarray, k: int = 5) -> List[Tuple[str, float]]:
        if not self.conn:
            return []
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT content, 1 - (embedding <=> %s::vector) AS similarity
                FROM user_embeddings
                WHERE user_id = %s
                ORDER BY embedding <=> %s::vector
                LIMIT %s
                """,
                (query_embedding.tolist(), user_id, query_embedding.tolist(), k),
            )
            rows = cur.fetchall()
            return [(row[0], float(row[1])) for row in rows]


