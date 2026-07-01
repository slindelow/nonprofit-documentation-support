"""
RAG (Retrieval-Augmented Generation) service.

Embeds a query and retrieves the top-k most semantically similar
knowledge chunks for the org.

Used by:
- ApplicationWriterAgent (one call per draft section)
- GrantDiscoveryAgent (org profile similarity against grant descriptions)
"""

from uuid import UUID

from openai import AsyncOpenAI

from app.config import settings

_openai = AsyncOpenAI(api_key=settings.openai_api_key)

EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSIONS = 1536


async def embed_text(text: str) -> list[float]:
    """Return a 1536-dim embedding vector for the input text."""
    response = await _openai.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text,
        dimensions=EMBEDDING_DIMENSIONS,
    )
    return response.data[0].embedding


async def retrieve_chunks(
    org_id: UUID,
    query: str,
    top_k: int = 5,
    doc_type_boost: list[str] | None = None,
) -> list[dict]:
    """
    Retrieve the top-k knowledge chunks for an org closest to the query.

    doc_type_boost: doc types to surface first (e.g. ['past_application']).
    These chunks are weighted higher in result ranking.

    Returns a list of dicts with keys: chunk_text, similarity, document_id, metadata
    """
    from sqlalchemy import text
    from app.db import get_async_session

    query_embedding = await embed_text(query)

    # Raw SQL for pgvector cosine similarity
    sql = text(
        """
        SELECT
            kc.id,
            kc.chunk_text,
            kc.metadata,
            kd.doc_type,
            kd.file_name,
            1 - (kc.embedding <=> :query_vec::vector) AS similarity
        FROM knowledge_chunks kc
        JOIN knowledge_documents kd ON kd.id = kc.document_id
        WHERE kc.org_id = :org_id
          AND kc.embedding IS NOT NULL
        ORDER BY kc.embedding <=> :query_vec::vector
        LIMIT :top_k
        """
    )

    async for session in get_async_session():
        result = await session.execute(
            sql,
            {
                "query_vec": str(query_embedding),
                "org_id": str(org_id),
                "top_k": top_k * 2,  # Fetch extra to allow boost reranking
            },
        )
        rows = result.mappings().all()

    # Apply boost: promote past_application chunks to top of results
    if doc_type_boost:
        boosted = [r for r in rows if r["doc_type"] in doc_type_boost]
        others = [r for r in rows if r["doc_type"] not in doc_type_boost]
        rows = (boosted + others)[:top_k]
    else:
        rows = list(rows)[:top_k]

    return [dict(r) for r in rows]
