#!/usr/bin/env python3
"""
Chunk extracted document text into segments suitable for embedding.

Strategy: 512-token chunks with 64-token overlap.
Respects paragraph boundaries where possible (avoids cutting mid-sentence).

Usage:
    python tools/knowledge_base/chunk_documents.py --text path/to/text.txt [--output path/to/chunks.json]
    echo "Some text..." | python tools/knowledge_base/chunk_documents.py

Outputs JSON array of chunks: [{chunk_index, chunk_text, token_count}]

Workflow: workflows/application_drafting.md
"""

import argparse
import json
import logging
import re
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

CHUNK_SIZE_TOKENS = 512
OVERLAP_TOKENS = 64
# Approximate: 1 token ≈ 4 characters for English text
CHARS_PER_TOKEN = 4


def estimate_tokens(text: str) -> int:
    return len(text) // CHARS_PER_TOKEN


def split_into_paragraphs(text: str) -> list[str]:
    """Split text into paragraphs on double newlines."""
    paragraphs = [p.strip() for p in re.split(r"\n\n+", text)]
    return [p for p in paragraphs if p]


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE_TOKENS, overlap: int = OVERLAP_TOKENS) -> list[dict]:
    """
    Chunk text into segments of approximately chunk_size tokens with overlap.

    Strategy:
    1. Split into paragraphs
    2. Fill chunks by adding paragraphs until chunk_size is reached
    3. Carry over the last overlap_tokens worth of content to the next chunk
    """
    paragraphs = split_into_paragraphs(text)
    chunks = []
    current_chunk_parts: list[str] = []
    current_tokens = 0
    chunk_index = 0

    for para in paragraphs:
        para_tokens = estimate_tokens(para)

        # If a single paragraph is larger than the chunk size, split it by sentences
        if para_tokens > chunk_size:
            sentences = re.split(r"(?<=[.!?])\s+", para)
            for sentence in sentences:
                sent_tokens = estimate_tokens(sentence)
                if current_tokens + sent_tokens > chunk_size and current_chunk_parts:
                    # Save current chunk
                    chunk_text_str = " ".join(current_chunk_parts)
                    chunks.append({
                        "chunk_index": chunk_index,
                        "chunk_text": chunk_text_str,
                        "token_count": estimate_tokens(chunk_text_str),
                    })
                    chunk_index += 1
                    # Overlap: keep last overlap_tokens of text
                    overlap_text = chunk_text_str[-(overlap * CHARS_PER_TOKEN):]
                    current_chunk_parts = [overlap_text] if overlap_text else []
                    current_tokens = estimate_tokens(overlap_text)
                current_chunk_parts.append(sentence)
                current_tokens += sent_tokens
        else:
            if current_tokens + para_tokens > chunk_size and current_chunk_parts:
                # Save current chunk
                chunk_text_str = "\n\n".join(current_chunk_parts)
                chunks.append({
                    "chunk_index": chunk_index,
                    "chunk_text": chunk_text_str,
                    "token_count": estimate_tokens(chunk_text_str),
                })
                chunk_index += 1
                # Overlap: keep last overlap_tokens of content
                overlap_text = chunk_text_str[-(overlap * CHARS_PER_TOKEN):]
                current_chunk_parts = [overlap_text] if overlap_text else []
                current_tokens = estimate_tokens(overlap_text)
            current_chunk_parts.append(para)
            current_tokens += para_tokens

    # Save final chunk
    if current_chunk_parts:
        chunk_text_str = "\n\n".join(current_chunk_parts)
        chunks.append({
            "chunk_index": chunk_index,
            "chunk_text": chunk_text_str,
            "token_count": estimate_tokens(chunk_text_str),
        })

    log.info("Created %d chunks from %d characters", len(chunks), len(text))
    return chunks


def main():
    parser = argparse.ArgumentParser(description="Chunk document text for embedding")
    parser.add_argument("--text", help="Path to text file (default: stdin)")
    parser.add_argument("--output", help="Output JSON file (default: stdout)")
    parser.add_argument("--chunk-size", type=int, default=CHUNK_SIZE_TOKENS)
    parser.add_argument("--overlap", type=int, default=OVERLAP_TOKENS)
    args = parser.parse_args()

    if args.text:
        text = Path(args.text).read_text(encoding="utf-8")
    else:
        text = sys.stdin.read()

    chunks = chunk_text(text, chunk_size=args.chunk_size, overlap=args.overlap)

    output = json.dumps(chunks, indent=2, ensure_ascii=False)
    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
    else:
        print(output)


if __name__ == "__main__":
    main()
