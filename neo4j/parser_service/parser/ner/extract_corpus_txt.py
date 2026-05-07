from __future__ import annotations

from pathlib import Path
from pypdf import PdfReader
import re


def clean_text(text: str) -> str:
    text = text.replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_pdf_text(pdf_path: Path) -> str:
    reader = PdfReader(str(pdf_path))
    pages = []

    for page in reader.pages:
        try:
            txt = page.extract_text() or ""
        except Exception:
            txt = ""
        if txt.strip():
            pages.append(txt)

    return clean_text("\n\n".join(pages))


def main() -> None:
    input_dir = Path("parser/samples/corpus_pdfs")
    output_dir = Path("parser/samples/corpus_txt")
    output_dir.mkdir(parents=True, exist_ok=True)

    pdf_files = sorted(input_dir.glob("*.pdf"))
    if not pdf_files:
        print("No PDF files found in", input_dir)
        return

    for pdf_file in pdf_files:
        text = extract_pdf_text(pdf_file)
        out_file = output_dir / f"{pdf_file.stem}.txt"
        out_file.write_text(text, encoding="utf-8")
        print(f"{pdf_file.name} -> {out_file.name} | chars={len(text)}")

    print("Done.")


if __name__ == "__main__":
    main()
