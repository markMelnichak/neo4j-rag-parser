from __future__ import annotations

from pathlib import Path
import json
import random
from typing import Any

import spacy
from spacy.tokens import DocBin


LABEL_PRIORITY = {
    "MODEL": 5,
    "FRAMEWORK": 4,
    "METHOD": 3,
    "TASK": 2,
    "CONCEPT": 1,
}


def load_records(path: Path) -> list[dict[str, Any]]:
    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            records.append(json.loads(line))
    return records


def overlaps(a_start: int, a_end: int, b_start: int, b_end: int) -> bool:
    return max(a_start, b_start) < min(a_end, b_end)


def remove_overlapping_entities(entities: list[list[Any]]) -> list[list[Any]]:
    cleaned = []

    normalized = []
    for ent in entities:
        if not isinstance(ent, list) or len(ent) != 3:
            continue

        start, end, label = ent

        try:
            start = int(start)
            end = int(end)
        except Exception:
            continue

        label = str(label).upper()

        if start >= end:
            continue

        length = end - start
        priority = LABEL_PRIORITY.get(label, 0)
        normalized.append([start, end, label, length, priority])

    # Сначала оставляем более длинные span, при равенстве — более приоритетные label
    normalized.sort(key=lambda x: (x[3], x[4]), reverse=True)

    for start, end, label, _, _ in normalized:
        conflict = False

        for ex_start, ex_end, _ in cleaned:
            if overlaps(start, end, ex_start, ex_end):
                conflict = True
                break

        if not conflict:
            cleaned.append([start, end, label])

    cleaned.sort(key=lambda x: (x[0], x[1], x[2]))
    return cleaned


def main() -> None:
    src = Path("parser/ner/annotations/annotations.jsonl")
    out_dir = Path("parser/ner/data")
    out_dir.mkdir(parents=True, exist_ok=True)

    if not src.exists():
        print("Нет файла разметки:", src)
        return

    records = load_records(src)

    fixed_records = []
    removed_total = 0

    for record in records:
        original_entities = record.get("entities", [])
        cleaned_entities = remove_overlapping_entities(original_entities)

        removed_total += max(0, len(original_entities) - len(cleaned_entities))

        if not cleaned_entities:
            continue

        fixed_records.append({
            "id": record.get("id"),
            "text": record.get("text", ""),
            "entities": cleaned_entities,
        })

    random.seed(42)
    random.shuffle(fixed_records)

    split_idx = max(1, int(len(fixed_records) * 0.8))
    train_records = fixed_records[:split_idx]
    dev_records = fixed_records[split_idx:]

    nlp = spacy.blank("xx")

    for dataset, name in [(train_records, "train"), (dev_records, "dev")]:
        db = DocBin()
        skipped_spans = 0

        for record in dataset:
            text = record["text"]
            ents_raw = record["entities"]
            doc = nlp.make_doc(text)

            spans = []
            occupied_tokens = set()

            for start, end, label in ents_raw:
                span = doc.char_span(start, end, label=label, alignment_mode="contract")

                if span is None:
                    skipped_spans += 1
                    continue

                token_range = set(range(span.start, span.end))
                if occupied_tokens.intersection(token_range):
                    skipped_spans += 1
                    continue

                occupied_tokens.update(token_range)
                spans.append(span)

            doc.ents = spans
            db.add(doc)

        out_path = out_dir / f"{name}.spacy"
        db.to_disk(out_path)
        print(f"Saved: {out_path} | records={len(dataset)} | skipped_spans={skipped_spans}")

    print(f"Input records: {len(records)}")
    print(f"Used records: {len(fixed_records)}")
    print(f"Removed overlapping entities: {removed_total}")


if __name__ == "__main__":
    main()
