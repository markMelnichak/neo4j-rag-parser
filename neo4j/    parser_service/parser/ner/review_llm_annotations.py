from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


LABELS = ["MODEL", "TASK", "METHOD", "FRAMEWORK", "CONCEPT"]


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


def append_jsonl(path: Path, obj: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def find_all_spans(text: str, entity_text: str) -> list[tuple[int, int]]:
    spans = []
    start = 0

    while True:
        idx = text.find(entity_text, start)
        if idx == -1:
            break
        spans.append((idx, idx + len(entity_text)))
        start = idx + len(entity_text)

    return spans


def show_entities(text: str, entities: list[list[Any]]) -> None:
    if not entities:
        print("Сущностей нет.")
        return

    for i, item in enumerate(entities, start=1):
        start, end, label = item
        value = text[start:end]
        print(f"{i}. {label}|{value} [{start}:{end}]")


def add_manual_entity(text: str, entities: list[list[Any]]) -> None:
    cmd = input("Добавить вручную LABEL|TEXT: ").strip()

    if "|" not in cmd:
        print("Неверный формат.")
        return

    label, value = [x.strip() for x in cmd.split("|", 1)]
    label = label.upper()

    if label not in LABELS:
        print("Неизвестная метка.")
        return

    spans = find_all_spans(text, value)
    if not spans:
        print("Такой текст не найден во фрагменте.")
        return

    if len(spans) == 1:
        start, end = spans[0]
        entities.append([start, end, label])
        print("Добавлено.")
        return

    print("Найдено несколько совпадений:")
    for i, (start, end) in enumerate(spans, start=1):
        frag = text[max(0, start - 40): min(len(text), end + 40)]
        print(f"{i}. {start}:{end} ...{frag}...")

    choice = input("Номер или all: ").strip()

    if choice == "all":
        for start, end in spans:
            entities.append([start, end, label])
        print("Добавлены все.")
        return

    try:
        idx = int(choice) - 1
        start, end = spans[idx]
        entities.append([start, end, label])
        print("Добавлено.")
    except Exception:
        print("Некорректный выбор.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="parser/ner/annotations/llm_annotations.jsonl")
    parser.add_argument("--output", default="parser/ner/annotations/annotations.jsonl")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    source_records = load_jsonl(input_path)
    reviewed = {r["id"] for r in load_jsonl(output_path)}

    for record in source_records:
        rel_id = record["id"]
        if rel_id in reviewed:
            continue

        text = record["text"]
        entities = [list(x) for x in record.get("entities", [])]

        print("\n" + "=" * 100)
        print("ID:", rel_id)
        print("STATUS:", record.get("status"))
        print("-" * 100)
        print(text)
        print("-" * 100)
        print("Предложенная разметка:")
        show_entities(text, entities)

        while True:
            print("\nКоманды:")
            print("a = accept")
            print("d = delete entity by number")
            print("m = manual add")
            print("s = skip fragment")
            print("show = show entities")
            print("text = show text")
            cmd = input(">>> ").strip().lower()

            if cmd == "a":
                entities = sorted(set(tuple(x) for x in entities), key=lambda x: (x[0], x[1], x[2]))
                obj = {
                    "id": rel_id,
                    "text": text,
                    "entities": [list(x) for x in entities],
                    "status": "reviewed",
                    "source": "llm_reviewed",
                }
                append_jsonl(output_path, obj)
                reviewed.add(rel_id)
                print("Сохранено.")
                break

            if cmd == "s":
                obj = {
                    "id": rel_id,
                    "text": text,
                    "entities": [],
                    "status": "reviewed_skipped",
                    "source": "llm_reviewed",
                }
                append_jsonl(output_path, obj)
                reviewed.add(rel_id)
                print("Пропущено.")
                break

            if cmd == "d":
                show_entities(text, entities)
                num = input("Номер удалить: ").strip()
                try:
                    idx = int(num) - 1
                    removed = entities.pop(idx)
                    print("Удалено:", removed)
                except Exception:
                    print("Некорректный номер.")
                continue

            if cmd == "m":
                add_manual_entity(text, entities)
                continue

            if cmd == "show":
                show_entities(text, entities)
                continue

            if cmd == "text":
                print(text)
                continue

            print("Неизвестная команда.")

    print("Review finished.")
    print("Output:", output_path)


if __name__ == "__main__":
    main()
