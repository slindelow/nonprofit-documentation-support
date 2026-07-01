#!/usr/bin/env python3
"""
Extract text from uploaded documents (PDF, DOCX, TXT).

Usage:
    python tools/knowledge_base/extract_text.py --file path/to/document.pdf [--output path/to/output.txt]

Supports:
    - PDF: pdfplumber (preferred, handles columns/tables), pypdf fallback, pytesseract for scans
    - DOCX: python-docx
    - TXT: direct read

Workflow: workflows/application_drafting.md
See also: skills/SKILL (5).md (PDF), skills/SKILL (4).md (DOCX)
"""

import argparse
import logging
import os
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)


def extract_pdf(file_path: Path) -> str:
    """Extract text from PDF using pdfplumber. Falls back to OCR if needed."""
    import pdfplumber

    text_parts = []

    with pdfplumber.open(file_path) as pdf:
        for i, page in enumerate(pdf.pages):
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
            else:
                log.debug("Page %d: no text extracted, may need OCR", i + 1)

    full_text = "\n\n".join(text_parts).strip()

    # If we got almost nothing, try OCR
    if len(full_text) < 100:
        log.info("Text extraction yielded very little text. Attempting OCR...")
        full_text = extract_pdf_ocr(file_path)

    return full_text


def extract_pdf_ocr(file_path: Path) -> str:
    """Extract text from scanned PDF using pytesseract."""
    try:
        from pdf2image import convert_from_path
        import pytesseract

        images = convert_from_path(str(file_path), dpi=300)
        text_parts = []
        for i, image in enumerate(images):
            log.info("OCR processing page %d/%d", i + 1, len(images))
            text = pytesseract.image_to_string(image, lang="eng")
            text_parts.append(text)
        return "\n\n".join(text_parts).strip()
    except ImportError:
        log.error("pdf2image or pytesseract not installed. Cannot OCR this file.")
        return ""


def extract_docx(file_path: Path) -> str:
    """Extract text from DOCX using python-docx. See skills/SKILL (4).md."""
    from docx import Document

    doc = Document(str(file_path))
    paragraphs = []

    for para in doc.paragraphs:
        if para.text.strip():
            paragraphs.append(para.text.strip())

    # Also extract text from tables
    for table in doc.tables:
        for row in table.rows:
            row_text = " | ".join(
                cell.text.strip() for cell in row.cells if cell.text.strip()
            )
            if row_text:
                paragraphs.append(row_text)

    return "\n\n".join(paragraphs)


def extract_txt(file_path: Path) -> str:
    """Read plain text file."""
    return file_path.read_text(encoding="utf-8", errors="replace")


def extract_text(file_path: str | Path) -> str:
    """
    Main entry point. Detects file type and extracts text.

    Returns the full text content of the document.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    suffix = path.suffix.lower()

    if suffix == ".pdf":
        log.info("Extracting text from PDF: %s", path.name)
        text = extract_pdf(path)
    elif suffix in (".docx", ".doc"):
        log.info("Extracting text from DOCX: %s", path.name)
        text = extract_docx(path)
    elif suffix == ".txt":
        log.info("Reading text file: %s", path.name)
        text = extract_txt(path)
    else:
        raise ValueError(f"Unsupported file type: {suffix}. Supported: .pdf, .docx, .txt")

    # Basic cleanup
    import re
    text = re.sub(r"\n{3,}", "\n\n", text)  # Collapse 3+ newlines
    text = re.sub(r" {2,}", " ", text)       # Collapse multiple spaces

    log.info("Extracted %d characters (%d words)", len(text), len(text.split()))
    return text


def main():
    parser = argparse.ArgumentParser(description="Extract text from a document")
    parser.add_argument("--file", required=True, help="Path to the document file")
    parser.add_argument("--output", help="Output text file (default: stdout)")
    args = parser.parse_args()

    text = extract_text(args.file)

    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
        log.info("Written to %s", args.output)
    else:
        print(text)


if __name__ == "__main__":
    main()
