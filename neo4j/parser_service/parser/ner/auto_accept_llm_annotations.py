from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


ALLOWED_LABELS = {"MODEL", "TASK", "METHOD", "FRAMEWORK", "CONCEPT"}

BAD_EXACT = {
    "data", "model", "method", "algorithm", "information", "system", "task", "quality",
    "данные", "модель", "метод", "алгоритм", "информация", "система", "задача", "качество",
    "объект", "объекты", "множество", "значение", "значения", "класс", "классы",
    "рисунок", "таблица", "литература", "источник", "формула",
}

BAD_SUBSTRINGS = [
    "x→y",
    "х→y",
    "x -> y",
    "х -> y",
    "рисунок",
    "таблица",
    "isbn",
    "удк",
    "ббк",
    "д-р",
    "канд.",
    "стр.",
]

BAD_CHARS = [
    "ϵ", "∈", "{", "}", "=", "…", "№"
]


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []

    result = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            result.append(json.loads(line))
    return result


def save_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def entity_text(text: str, ent: list[Any]) -> str:
    start, end, _ = ent
    return text[int(start):int(end)].strip()


def is_bad_entity(value: str, label: str) -> bool:
    raw = value.strip()
    low = raw.lower()

    if not raw:
        return True

    if len(raw) < 3:
        return True

    if len(raw) > 80:
        return True

    if low in BAD_EXACT:
        return True

    if any(x in low for x in BAD_SUBSTRINGS):
        return True

    if any(ch in raw for ch in BAD_CHARS):
        return True

    if raw.count(" ") > 6:
        return True

    if raw.endswith((",", ".", ";", ":", "-", "–")):
        return True

    if raw.startswith(("-", "–", ",", ".", ";", ":")):
        return True

    # Отсекаем явно битые русские куски вроде "Qwen реализуется", "Mistral часто"
    words = raw.split()
    if len(words) >= 2:
        last = words[-1].lower()
        if last in {"часто", "реализуется", "связан", "связана", "является", "используется", "позволяет"}:
            return True

    # Не принимаем одиночные слишком общие русские существительные
    if label in {"METHOD", "CONCEPT", "TASK"} and len(words) == 1:
        if low in {
            "классификация", "кластеризация", "регрессия", "аппроксимация",
            "оптимизация", "распознавание"
        }:
            return False

        if re.fullmatch(r"[а-яё]+", low) and len(low) < 8:
            return True

    return False


def clean_record(record: dict[str, Any]) -> dict[str, Any] | None:
    text = record.get("text", "")
    entities = record.get("entities", [])

    if not isinstance(text, str) or not text.strip():
        return None

    cleaned = []
    seen = set()

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

        if label not in ALLOWED_LABELS:
            continue

        if start < 0 or end > len(text) or start >= end:
            continue

        value = text[start:end].strip()

        if is_bad_entity(value, label):
            continue

        key = (start, end, label)
        if key in seen:
            continue

        seen.add(key)
        cleaned.append([start, end, label])

    # Если после фильтрации нет сущностей, можно не включать фрагмент в обучение
    if not cleaned:
        return None

    return {
        "id": record["id"],
        "text": text,
        "entities": sorted(cleaned, key=lambda x: (x[0], x[1], x[2])),
        "status": "auto_accepted",
        "source": "llm_auto_filtered",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="parser/ner/annotations/llm_annotations.jsonl")
    parser.add_argument("--output", default="parser/ner/annotations/annotations.jsonl")
    parser.add_argument("--min-entities", type=int, default=1)
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    records = load_jsonl(input_path)

    accepted = []
    skipped = 0

    for record in records:
        cleaned = clean_record(record)

        if cleaned is None:
            skipped += 1
            continue

        if len(cleaned["entities"]) < args.min_entities:
            skipped += 1
            continue

        accepted.append(cleaned)

    save_jsonl(output_path, accepted)

    print(f"Input records: {len(records)}")
    print(f"Accepted records: {len(accepted)}")
    print(f"Skipped records: {skipped}")
    print(f"Output: {output_path}")


if __name__ == "__main__":
    main()
