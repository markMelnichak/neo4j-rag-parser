from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Tuple

from pypdf import PdfReader


@dataclass
class ExtractedDocument:
    source_path: Path
    txt_path: Path
    md_path: Path
    raw_text: str


def _clean_pdf_text(text: str) -> str:
    text = text.replace("\u00ad", "")
    text = text.replace("\r", "\n")
    lines = [line.rstrip() for line in text.split("\n")]
    cleaned_lines = []
    prev_blank = False
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if not prev_blank:
                cleaned_lines.append("")
            prev_blank = True
            continue
        cleaned_lines.append(" ".join(stripped.split()))
        prev_blank = False
    return "\n".join(cleaned_lines).strip()


def _txt_to_markdown(text: str) -> str:
    parts = [part.strip() for part in text.split("\n\n") if part.strip()]
    md_blocks = []
    for part in parts:
        if len(part) < 120 and part == part.title():
            md_blocks.append(f"## {part}")
        else:
            md_blocks.append(part)
    return "\n\n".join(md_blocks).strip() + "\n"


def extract_pdf_to_intermediate(
    pdf_path: Path,
    output_dir: Path,
) -> ExtractedDocument:
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    output_dir.mkdir(parents=True, exist_ok=True)

    reader = PdfReader(str(pdf_path))
    page_texts = []

    for page in reader.pages:
        text = page.extract_text() or ""
        page_texts.append(text)

    raw_text = "\n\n".join(page_texts).strip()
    cleaned_text = _clean_pdf_text(raw_text)

    if not cleaned_text:
        raise ValueError(
            "Не удалось извлечь текст из PDF. "
            "Скорее всего PDF является сканом или содержит слишком сложную верстку."
        )

    stem = pdf_path.stem
    txt_path = output_dir / f"{stem}.txt"
    md_path = output_dir / f"{stem}.md"

    txt_path.write_text(cleaned_text, encoding="utf-8")
    md_path.write_text(_txt_to_markdown(cleaned_text), encoding="utf-8")

    return ExtractedDocument(
        source_path=pdf_path,
        txt_path=txt_path,
        md_path=md_path,
        raw_text=cleaned_text,
    )


def extract_text_from_supported_file(
    input_path: Path,
    output_dir: Path,
) -> Tuple[str, Path, Path]:
    suffix = input_path.suffix.lower()

    if suffix == ".pdf":
        doc = extract_pdf_to_intermediate(input_path, output_dir)
        return doc.raw_text, doc.txt_path, doc.md_path

    if suffix in {".txt", ".md"}:
        text = input_path.read_text(encoding="utf-8")
        output_dir.mkdir(parents=True, exist_ok=True)
        txt_path = output_dir / f"{input_path.stem}.txt"
        md_path = output_dir / f"{input_path.stem}.md"
        txt_path.write_text(text, encoding="utf-8")
        md_path.write_text(text, encoding="utf-8")
        return text, txt_path, md_path

    raise ValueError(f"Unsupported file type: {suffix}")
