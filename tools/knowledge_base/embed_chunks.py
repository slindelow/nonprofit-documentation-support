#!/usr/bin/env python3
"""
Embed text chunks using OpenAI text-embedding-3-small.

Usage:
    python tools/knowledge_base/embed_chunks.py \
        --chunks path/to/chunks.json \
        --output path/to/chunks_with_embeddings.json

Reads a JSON array of {chunk_index, chunk_text, token_count} from --chunks or stdin.
Outputs the same array with an added "embedding" field (list of 1536 floats).

Processes in batches of 100 to respect API limits.

Workflow: workflows/application_drafting.md
"""

import argparse
import json
import logging
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSIONS = 1536
BATCH_SIZE = 100


def embed_batch(texts: list[str], client) -> list[list[float]]:
    """Embed a batch of texts. Returns a list of embedding vectors."""
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=texts,
        dimensions=EMBEDDING_DIMENSIONS,
    )
    return [item.embedding for item in response.data]


def embed_chunks(chunks: list[dict]) -> list[dict]:
    """Add embeddings to all chunks. Processes in batches."""
    from openai import OpenAI

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    total = len(chunks)
    log.info("Embedding %d chunks using %s", total, EMBEDDING_MODEL)

    for i in range(0, total, BATCH_SIZE):
        batch = chunks[i : i + BATCH_SIZE]
        texts = [c["chunk_text"] for c in batch]

        try:
            embeddings = embed_batch(texts, client)
            for chunk, embedding in zip(batch, embeddings):
                chunk["embedding"] = embedding
            log.info("Embedded chunks %d–%d / %d", i + 1, min(i + BATCH_SIZE, total), total)
        except Exception as e:
            log.error("Embedding batch %d failed: %s", i // BATCH_SIZE + 1, e)
            # On failure, leave embedding as None so we can retry
            for chunk in batch:
                chunk["embedding"] = None
            time.sleep(5)

    return chunks


def main():
    parser = argparse.ArgumentParser(description="Embed document chunks via OpenAI")
    parser.add_argument("--chunks", help="Path to chunks JSON file (default: stdin)")
    parser.add_argument("--output", help="Output JSON file (default: stdout)")
    args = parser.parse_args()

    if args.chunks:
        chunks = json.loads(Path(args.chunks).read_text())
    else:
        chunks = json.load(sys.stdin)

    chunks_with_embeddings = embed_chunks(chunks)

    success = sum(1 for c in chunks_with_embeddings if c.get("embedding"))
    log.info("Successfully embedded %d/%d chunks", success, len(chunks_with_embeddings))

    output = json.dumps(chunks_with_embeddings)
    if args.output:
        Path(args.output).write_text(output)
    else:
        print(output)


if __name__ == "__main__":
    main()
