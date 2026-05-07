from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str]) -> None:
    print("\n" + "=" * 100)
    print("RUN:", " ".join(cmd))
    print("=" * 100)
    subprocess.run(cmd, check=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fragments-dir", default="parser/samples/corpus_fragments")
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--sleep", type=float, default=0.2)
    parser.add_argument("--reset-llm", action="store_true")
    parser.add_argument("--reset-final", action="store_true")
    args = parser.parse_args()

    llm_path = Path("parser/ner/annotations/llm_annotations.jsonl")
    final_path = Path("parser/ner/annotations/annotations.jsonl")

    if args.reset_llm and llm_path.exists():
        llm_path.unlink()
        print("Deleted:", llm_path)

    if args.reset_final and final_path.exists():
        final_path.unlink()
        print("Deleted:", final_path)

    run([
        sys.executable,
        "-m",
        "parser.ner.llm_annotate_fragments",
        "--fragments-dir",
        args.fragments_dir,
        "--limit",
        str(args.limit),
        "--sleep",
        str(args.sleep),
    ])

    run([
        sys.executable,
        "-m",
        "parser.ner.auto_accept_llm_annotations",
    ])

    run([
        sys.executable,
        "-m",
        "parser.ner.annotations_to_docbin",
    ])

    run([
        sys.executable,
        "-m",
        "parser.ner.train_spacy_ner",
    ])

    print("\nAUTO TRAIN FINISHED")
    print("Model path: parser/models/ner_model")


if __name__ == "__main__":
    main()
