from __future__ import annotations

from pathlib import Path
import argparse
import re


def normalize_text(text: str) -> str:
    text = text.replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def split_into_fragments(text: str, min_len: int = 500, max_len: int = 1400) -> list[str]:
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    fragments: list[str] = []
    buffer = ""

    for p in paragraphs:
        candidate = f"{buffer}\n\n{p}".strip() if buffer else p

        if len(candidate) <= max_len:
            buffer = candidate
            continue

        if buffer and len(buffer) >= min_len:
            fragments.append(buffer.strip())
            buffer = p
        else:
            parts = re.split(r'(?<=[.!?])\s+', p)
            temp = ""
            for part in parts:
                cand = f"{temp} {part}".strip() if temp else part
                if len(cand) <= max_len:
                    temp = cand
                else:
                    if temp:
                        fragments.append(temp.strip())
                    temp = part
            buffer = temp

    if buffer.strip():
        fragments.append(buffer.strip())

    return [f for f in fragments if len(f) >= min_len // 2]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", default="parser/samples/corpus_txt")
    parser.add_argument("--output-dir", default="parser/samples/corpus_fragments")
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    txt_files = sorted(input_dir.glob("*.txt"))
    if not txt_files:
        print("No TXT files found in", input_dir)
        return

    for txt_file in txt_files:
        text = normalize_text(txt_file.read_text(encoding="utf-8", errors="ignore"))
        fragments = split_into_fragments(text)

        stem_dir = output_dir / txt_file.stem
        stem_dir.mkdir(parents=True, exist_ok=True)

        for idx, fragment in enumerate(fragments, start=1):
            out_file = stem_dir / f"{idx:04d}.txt"
            out_file.write_text(fragment, encoding="utf-8")

        print(f"{txt_file.name}: {len(fragments)} fragments -> {stem_dir}")


if __name__ == "__main__":
    main()
