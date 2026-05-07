from __future__ import annotations

import argparse
import json
import os
import re
import time
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv


LABELS = {"MODEL", "TASK", "METHOD", "FRAMEWORK", "CONCEPT"}

SYSTEM_PROMPT = """
You are an expert annotator for a custom NER dataset in Artificial Intelligence and Machine Learning.

Your task:
Extract named technical entities from the given text fragment.

Allowed labels only:
MODEL — names of AI/ML models or model families, e.g. BERT, GPT, LLaMA, ResNet, Transformer model only when used as model name.
TASK — AI/ML tasks, e.g. classification, regression, question answering, machine translation, image segmentation.
METHOD — algorithms, training methods, optimization methods, learning methods, e.g. backpropagation, fine-tuning, regularization, dropout, gradient descent.
FRAMEWORK — libraries, frameworks, platforms, tools, e.g. PyTorch, TensorFlow, Keras, OpenCV, scikit-learn.
CONCEPT — general AI/ML concepts, architectures, representations, theoretical notions, e.g. machine learning, neural network, embedding, feature space, overfitting.

Strict rules:
1. Return ONLY valid JSON.
2. Do not explain.
3. Do not invent entities.
4. Entity text must appear exactly in the input text.
5. Do not annotate authors, organizations, cities, ISBN, references, figure numbers, table numbers.
6. Do not annotate very generic words alone: data, model, method, algorithm, information, system, task, quality.
7. Prefer full technical terms over fragments.
8. For Russian text, annotate Russian terms exactly as written.
9. For English text, annotate English terms exactly as written.
10. If the fragment is broken, bibliographic, or useless, return an empty list.

Return JSON in this exact format:
{
  "entities": [
    {"text": "...", "label": "CONCEPT"},
    {"text": "...", "label": "METHOD"}
  ]
}
""".strip()


def load_existing(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}

    result: dict[str, dict[str, Any]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        obj = json.loads(line)
        result[obj["id"]] = obj
    return result


def append_jsonl(path: Path, obj: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def is_junk_fragment(text: str) -> bool:
    low = text.lower()

    junk_markers = [
        "isbn",
        "удк",
        "ббк",
        "рецензенты",
        "библиографический список",
        "литература",
        "copyright",
        "references",
        "arxiv:",
    ]

    if any(marker in low for marker in junk_markers):
        return True

    alpha_count = sum(ch.isalpha() for ch in text)
    if alpha_count < 120:
        return True

    broken_ratio = len(re.findall(r"\b[А-Яа-яA-Za-z]{1,2}\b", text)) / max(1, len(text.split()))
    if broken_ratio > 0.35:
        return True

    return False


def extract_json(raw: str) -> dict[str, Any]:
    raw = raw.strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", raw, flags=re.DOTALL)
    if not match:
        return {"entities": []}

    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return {"entities": []}


def call_llm(text: str, base_url: str, api_key: str, model: str, timeout: int = 120) -> dict[str, Any]:
    url = base_url.rstrip("/") + "/chat/completions"

    payload = {
        "model": model,
        "temperature": 0,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    "Annotate this fragment for NER training.\n\n"
                    "TEXT:\n"
                    f"{text}"
                ),
            },
        ],
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    response = requests.post(url, headers=headers, json=payload, timeout=timeout)
    response.raise_for_status()

    data = response.json()
    content = data["choices"][0]["message"]["content"]
    return extract_json(content)


def find_spans(text: str, entity_text: str) -> list[tuple[int, int]]:
    spans: list[tuple[int, int]] = []
    start = 0

    while True:
        idx = text.find(entity_text, start)
        if idx == -1:
            break
        spans.append((idx, idx + len(entity_text)))
        start = idx + len(entity_text)

    return spans


def normalize_entity_text(value: str) -> str:
    value = value.strip()
    value = re.sub(r"\s+", " ", value)
    value = value.strip(".,;:()[]{}«»\"'")
    return value


def validate_entities(text: str, entities: list[dict[str, Any]]) -> list[tuple[int, int, str, str]]:
    result: list[tuple[int, int, str, str]] = []
    seen: set[tuple[int, int, str]] = set()

    for ent in entities:
        raw_text = str(ent.get("text", "")).strip()
        label = str(ent.get("label", "")).strip().upper()

        if label not in LABELS:
            continue

        ent_text = normalize_entity_text(raw_text)
        if not ent_text:
            continue

        if len(ent_text) < 3:
            continue

        if ent_text.lower() in {
            "data",
            "model",
            "method",
            "algorithm",
            "information",
            "system",
            "task",
            "quality",
            "данные",
            "модель",
            "метод",
            "алгоритм",
            "система",
            "задача",
            "качество",
            "информация",
        }:
            continue

        spans = find_spans(text, ent_text)

        if not spans and raw_text != ent_text:
            spans = find_spans(text, raw_text)
            ent_text = raw_text

        for start, end in spans:
            key = (start, end, label)
            if key in seen:
                continue
            seen.add(key)
            result.append((start, end, label, ent_text))

    result.sort(key=lambda x: (x[0], x[1], x[2]))
    return result


def main() -> None:
    load_dotenv()

    parser = argparse.ArgumentParser()
    parser.add_argument("--fragments-dir", default="parser/samples/corpus_fragments")
    parser.add_argument("--output", default="parser/ner/annotations/llm_annotations.jsonl")
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--sleep", type=float, default=0.2)
    parser.add_argument("--min-chars", type=int, default=400)
    args = parser.parse_args()

    base_url = os.getenv("LLM_BASE_URL", "").strip()
    api_key = os.getenv("LLM_API_KEY", "").strip()
    model = os.getenv("LLM_MODEL", "").strip()

    if not base_url or not api_key or not model:
        raise RuntimeError("Set LLM_BASE_URL, LLM_API_KEY and LLM_MODEL in .env")

    fragments_dir = Path(args.fragments_dir)
    output_path = Path(args.output)

    existing = load_existing(output_path)
    files = sorted(fragments_dir.glob("*/*.txt"))

    processed = 0

    for file_path in files:
        rel_id = str(file_path.relative_to(fragments_dir))

        if rel_id in existing:
            continue

        text = file_path.read_text(encoding="utf-8", errors="ignore").strip()

        if len(text) < args.min_chars or is_junk_fragment(text):
            obj = {
                "id": rel_id,
                "text": text,
                "entities": [],
                "status": "auto_skipped",
                "source": "llm_preannotation",
            }
            append_jsonl(output_path, obj)
            print(f"SKIP | {rel_id}")
            processed += 1
        else:
            try:
                llm_result = call_llm(text, base_url=base_url, api_key=api_key, model=model)
                raw_entities = llm_result.get("entities", [])
                valid = validate_entities(text, raw_entities)

                obj = {
                    "id": rel_id,
                    "text": text,
                    "entities": [[start, end, label] for start, end, label, _ in valid],
                    "entity_texts": [
                        {"text": ent_text, "label": label, "start": start, "end": end}
                        for start, end, label, ent_text in valid
                    ],
                    "status": "llm_preannotated",
                    "source": "llm_preannotation",
                }

                append_jsonl(output_path, obj)
                print(f"OK   | {rel_id} | entities={len(valid)}")
                processed += 1
                time.sleep(args.sleep)

            except Exception as exc:
                obj = {
                    "id": rel_id,
                    "text": text,
                    "entities": [],
                    "status": "error",
                    "error": str(exc),
                    "source": "llm_preannotation",
                }
                append_jsonl(output_path, obj)
                print(f"ERR  | {rel_id} | {exc}")
                processed += 1

        if processed >= args.limit:
            break

    print(f"Done. processed={processed}")
    print(f"Output: {output_path}")


if __name__ == "__main__":
    main()
