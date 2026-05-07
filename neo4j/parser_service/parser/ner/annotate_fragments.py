from __future__ import annotations

from pathlib import Path
import argparse
import json
import re


LABELS = ["MODEL", "TASK", "METHOD", "FRAMEWORK", "CONCEPT"]

SEED_TERMS = {
    "MODEL": [
        "BERT", "RoBERTa", "GPT", "T5", "LLaMA", "Whisper", "U-Net",
        "Diffusion Model", "CLIP", "SAM", "Mistral", "Mixtral", "Qwen",
    ],
    "TASK": [
        "Question Answering", "Text Classification", "Machine Translation",
        "Summarization", "Text Generation", "Image Segmentation",
        "Image Retrieval", "Image Generation", "Speech Recognition",
        "Speech Translation", "Zero-Shot Classification",
        "Retrieval-Augmented Generation",
    ],
    "METHOD": [
        "Fine-tuning", "Instruction Tuning", "Masked Language Modeling",
        "Backpropagation", "Adam Optimizer", "LoRA", "RLHF",
        "Contrastive Learning", "Prompt Encoding", "Quantization",
        "Mixture of Experts", "Classifier-Free Guidance",
        "Feature Extraction", "Preference Optimization",
        "Parameter-Efficient Fine-Tuning",
    ],
    "FRAMEWORK": [
        "PyTorch", "TensorFlow", "Hugging Face Transformers",
        "ONNX Runtime", "vLLM",
    ],
    "CONCEPT": [
        "Transformer", "Neural Network", "Embedding", "Tokenization",
        "Attention", "Self-Attention", "Context Window", "Vector Index",
        "Joint Embedding Space", "Latent Space", "Generative Model",
        "Sparse Routing", "Feature Map", "Mask Representation",
        "машинное обучение", "искусственный интеллект",
        "Интеллектуальный анализ данных", "экспертных систем",
    ],
}


def load_existing(path: Path) -> dict[str, dict]:
    if not path.exists():
        return {}
    items: dict[str, dict] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        obj = json.loads(line)
        items[obj["id"]] = obj
    return items


def save_all(path: Path, items: dict[str, dict]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for key in sorted(items.keys()):
            f.write(json.dumps(items[key], ensure_ascii=False) + "\n")


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


def auto_candidates(text: str) -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []

    for label, terms in SEED_TERMS.items():
        for term in terms:
            if term in text:
                found.append((label, term))

    # простые дополнительные эвристики
    extra_patterns = [
        ("CONCEPT", r"\bмашинное обучение\b"),
        ("CONCEPT", r"\bискусственный интеллект\b"),
        ("CONCEPT", r"\bнейронн\w+\s+сет\w+\b"),
        ("TASK", r"\bклассификац\w+\b"),
        ("TASK", r"\bраспознаван\w+\b"),
        ("METHOD", r"\bоптимизац\w+\b"),
        ("FRAMEWORK", r"\bPyTorch\b"),
        ("FRAMEWORK", r"\bTensorFlow\b"),
    ]

    for label, pattern in extra_patterns:
        for m in re.finditer(pattern, text, flags=re.IGNORECASE):
            found.append((label, m.group(0)))

    # дедуп
    uniq = []
    seen = set()
    for item in found:
        key = (item[0], item[1].strip())
        if key not in seen:
            seen.add(key)
            uniq.append((item[0], item[1].strip()))

    uniq.sort(key=lambda x: (x[0], x[1].lower()))
    return uniq


def confirm_candidates(text: str) -> list[tuple[int, int, str]]:
    accepted: list[tuple[int, int, str]] = []
    candidates = auto_candidates(text)

    if not candidates:
        print("Автопредразметка ничего не нашла.")
        return accepted

    print("\nПредлагаемые сущности:")
    for idx, (label, value) in enumerate(candidates, start=1):
        print(f"{idx}. {label}|{value}")

    print("\nПодтверждение кандидатов:")
    print("y = оставить первое совпадение")
    print("a = оставить все совпадения")
    print("n = пропустить")
    print("e = ввести вручную позже")

    for label, value in candidates:
        spans = find_all_spans(text, value)
        if not spans:
            continue

        if len(spans) == 1:
            answer = input(f"[{label}] {value} -> оставить? (y/n/e): ").strip().lower()
            if answer == "y":
                start, end = spans[0]
                accepted.append((start, end, label))
            continue

        answer = input(f"[{label}] {value} -> найдено {len(spans)} совпадений (y/a/n/e): ").strip().lower()
        if answer == "y":
            start, end = spans[0]
            accepted.append((start, end, label))
        elif answer == "a":
            for start, end in spans:
                accepted.append((start, end, label))

    return accepted


def annotate_text(text: str) -> list[tuple[int, int, str]]:
    entities: list[tuple[int, int, str]] = []
    entities.extend(confirm_candidates(text))

    while True:
        print("\nВведите сущность вручную.")
        print("Формат: <LABEL>|<TEXT>")
        print("Пример: MODEL|BERT")
        print("Команды: /done /skip /labels /show")
        cmd = input(">>> ").strip()

        if cmd == "/done":
            break
        if cmd == "/skip":
            return []
        if cmd == "/labels":
            print("LABELS:", ", ".join(LABELS))
            continue
        if cmd == "/show":
            print(text)
            continue

        if "|" not in cmd:
            print("Неверный формат.")
            continue

        label, entity_text = [x.strip() for x in cmd.split("|", 1)]
        if label not in LABELS:
            print("Неизвестная метка.")
            continue

        spans = find_all_spans(text, entity_text)
        if not spans:
            print("Текст сущности не найден.")
            continue

        if len(spans) == 1:
            start, end = spans[0]
            entities.append((start, end, label))
            print(f"Добавлено: {label} | {entity_text} | {start}:{end}")
            continue

        print("Найдено несколько совпадений:")
        for i, (start, end) in enumerate(spans, start=1):
            fragment = text[max(0, start - 40): min(len(text), end + 40)]
            print(f"{i}. {start}:{end} -> ...{fragment}...")

        pick = input("Выбери номер или 'all': ").strip()
        if pick == "all":
            for start, end in spans:
                entities.append((start, end, label))
            print(f"Добавлено {len(spans)} совпадений")
            continue

        try:
            idx = int(pick) - 1
            start, end = spans[idx]
            entities.append((start, end, label))
            print(f"Добавлено: {label} | {entity_text} | {start}:{end}")
        except Exception:
            print("Некорректный выбор.")

    unique = sorted(set(entities), key=lambda x: (x[0], x[1], x[2]))
    return unique


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fragments-dir", default="parser/samples/corpus_fragments")
    parser.add_argument("--output", default="parser/ner/annotations/annotations.jsonl")
    args = parser.parse_args()

    fragments_dir = Path(args.fragments_dir)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    items = load_existing(output_path)
    files = sorted(fragments_dir.glob("*/*.txt"))

    if not files:
        print("Фрагменты не найдены:", fragments_dir)
        return

    for file_path in files:
        rel_id = str(file_path.relative_to(fragments_dir))
        if rel_id in items:
            continue

        text = file_path.read_text(encoding="utf-8", errors="ignore").strip()
        print("\n" + "=" * 100)
        print("ID:", rel_id)
        print("-" * 100)
        print(text)
        print("-" * 100)

        entities = annotate_text(text)
        items[rel_id] = {
            "id": rel_id,
            "text": text,
            "entities": entities,
        }
        save_all(output_path, items)
        print(f"Сохранено: {rel_id}")

    print("Разметка завершена:", output_path)


if __name__ == "__main__":
    main()
