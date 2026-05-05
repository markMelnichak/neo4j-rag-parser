from __future__ import annotations

from pathlib import Path
import argparse
import shutil


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", default="parser/samples/corpus_fragments")
    parser.add_argument("--output-dir", default="parser/samples/corpus_fragments_balanced")
    parser.add_argument("--limit-per-source", type=int, default=100)
    parser.add_argument("--reset", action="store_true")
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)

    if args.reset and output_dir.exists():
        shutil.rmtree(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    source_dirs = sorted([p for p in input_dir.iterdir() if p.is_dir()])

    if not source_dirs:
        print("No source fragment directories found:", input_dir)
        return

    total = 0

    for source_dir in source_dirs:
        files = sorted(source_dir.glob("*.txt"))
        selected = files[: args.limit_per_source]

        target_dir = output_dir / source_dir.name
        target_dir.mkdir(parents=True, exist_ok=True)

        for file_path in selected:
            shutil.copy2(file_path, target_dir / file_path.name)

        total += len(selected)
        print(f"{source_dir.name}: copied {len(selected)} / {len(files)}")

    print(f"Done. Total copied: {total}")
    print(f"Output: {output_dir}")


if __name__ == "__main__":
    main()
