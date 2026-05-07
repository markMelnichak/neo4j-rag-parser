from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Relation:
    from_name: str
    from_label: str
    rel_type: str
    to_name: str
    to_label: str
    evidence: str = ""
    confidence: float = 0.85
    rule: str = "rule"
    source: str = "rule"

    @property
    def type(self) -> str:
        return self.rel_type


ExtractedRelation = Relation


BAD_RELATION_TARGETS = {
    "ner",
    "embedding",
    "attention",
    "neural network",
    "transformer",
}

BAD_ENTITY_NAMES = {
    "uses masked language modeling",
    "llama uses swiglu",
    "uses vector index",
}

GENERAL_METHODS = {
    "fine-tuning",
    "parameter-efficient fine-tuning",
}

MODEL_FAMILIES = {
    "gpt",
    "bert",
    "llama",
    "mistral",
    "mixtral",
    "bart",
    "roberta",
    "clip",
    "sam",
    "whisper",
    "qwen",
    "deepseek",
}


def _get(obj: Any, name: str, default: Any = None) -> Any:
    if isinstance(obj, dict):
        return obj.get(name, default)
    return getattr(obj, name, default)


def _entity_name(entity: Any) -> str:
    canonical = _get(entity, "canonical", None)
    text = _get(entity, "text", None)
    name = canonical or text or ""
    return str(name).strip()


def _entity_label(entity: Any) -> str:
    label = _get(entity, "label", "")
    return str(label).strip()


def _normalize_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _norm_key(text: str) -> str:
    text = text.lower().replace("ё", "е")
    text = re.sub(r"[^\wа-яА-ЯёЁ+#.\- ]+", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _split_sentences(text: str) -> list[str]:
    text = _normalize_spaces(text)
    parts = re.split(r"(?<=[.!?])\s+|\n+", text)
    return [p.strip() for p in parts if len(p.strip()) > 10]


def _contains_entity(sentence: str, name: str) -> bool:
    if not name:
        return False

    pattern = r"(?<![\wА-Яа-яёЁ])" + re.escape(name) + r"(?![\wА-Яа-яёЁ])"
    if re.search(pattern, sentence, flags=re.IGNORECASE):
        return True

    return _norm_key(name) in _norm_key(sentence)


def _find_entities_in_sentence(sentence: str, entities: list[Any]) -> list[dict[str, str]]:
    found: list[dict[str, str]] = []

    for ent in entities:
        name = _entity_name(ent)
        label = _entity_label(ent)

        if not name or not label:
            continue

        if _norm_key(name) in BAD_ENTITY_NAMES:
            continue

        if _contains_entity(sentence, name):
            found.append({"name": name, "label": label})

    found.sort(key=lambda x: len(x["name"]), reverse=True)

    result: list[dict[str, str]] = []
    seen: set[str] = set()

    for item in found:
        key = _norm_key(item["name"])
        if key in seen:
            continue
        seen.add(key)
        result.append(item)

    return result


def _main_subject(items: list[dict[str, str]]) -> dict[str, str] | None:
    priority = {
        "Model": 1,
        "Framework": 2,
        "Method": 3,
        "Concept": 4,
        "Task": 5,
    }

    sorted_items = sorted(items, key=lambda x: priority.get(x["label"], 99))
    return sorted_items[0] if sorted_items else None


def _has_any(sentence: str, markers: list[str]) -> bool:
    s = _norm_key(sentence)
    return any(_norm_key(marker) in s for marker in markers)


def _same_model_family(a: str, b: str) -> bool:
    ak = _norm_key(a)
    bk = _norm_key(b)

    for family in MODEL_FAMILIES:
        if family in ak and family in bk:
            return True

    return False


def _is_bad_target(name: str) -> bool:
    key = _norm_key(name)
    return key in BAD_RELATION_TARGETS


def _allowed_relation(
    source_label: str,
    rel_type: str,
    target_label: str,
    source_name: str,
    target_name: str,
) -> bool:
    source_key = _norm_key(source_name)
    target_key = _norm_key(target_name)

    if source_key == target_key:
        return False

    if source_key in BAD_ENTITY_NAMES or target_key in BAD_ENTITY_NAMES:
        return False

    # Общие слишком широкие / вредные цели для строгих связей.
    bad_exact_targets = {
        "ner",
        "attention",
        "embedding",
        "neural network",
        "vector search",
        "rag",
        "llamaindex",
        "langchain",
        "hugging face transformers",
    }

    bad_is_a_targets = {
        "ner",
        "vector search",
        "rag",
        "llamaindex",
        "langchain",
        "hugging face transformers",
        "qdrant",
        "milvus",
        "weaviate",
    }

    allowed_model_concepts = {
        "transformer",
        "transformer architecture",
        "transformer decoder architecture",
        "neural network",
        "mixture of experts",
        "contrastive learning",
    }

    allowed_model_methods = {
        "masked language modeling",
        "self-attention",
        "swiGLU activation function".lower(),
        "rotary positional embeddings",
        "mixture of experts",
        "contrastive learning",
        "lora",
        "qlora",
        "fine-tuning",
        "parameter-efficient fine-tuning",
        "quantization",
    }

    if rel_type == "IS_A":
        if target_label == "Task":
            return False

        if target_key in bad_is_a_targets:
            return False

        if source_label == "Model":
            if target_label == "Model":
                return _same_model_family(source_name, target_name)

            if target_label == "Concept":
                return target_key in allowed_model_concepts

            if target_label == "Method":
                return target_key in {"mixture of experts", "contrastive learning"}

            return False

        if source_label == "Method":
            if target_label == "Method":
                # LoRA -> Fine-tuning да, но Quantization -> LoRA нет.
                if source_key == "parameter-efficient fine-tuning" and target_key in {"fine-tuning", "lora"}:
                    return True
                if source_key == "qlora" and target_key in {"lora", "quantization", "fine-tuning"}:
                    return True
                return False

            if target_label == "Concept":
                return target_key not in bad_exact_targets

            return False

        # Framework IS_A Vector Search почти всегда мусор.
        if source_label == "Framework":
            return False

        return False

    if rel_type == "USES":
        if target_label == "Task":
            return False

        if target_key in bad_exact_targets:
            return False

        if source_label == "Model":
            if target_label == "Framework":
                # Модель не "использует" библиотеку в онтологическом смысле.
                return False

            if target_label == "Method":
                return target_key in allowed_model_methods

            if target_label == "Concept":
                return target_key in {
                    "transformer architecture",
                    "transformer decoder architecture",
                    "context window",
                    "joint embedding space",
                    "mask representation",
                    "vector index",
                }

            return False

        if source_label == "Method":
            if target_label == "Framework":
                return False

            if target_label == "Method":
                # Запрещаем обратные странные связи Quantization -> LoRA.
                if source_key == "quantization" and target_key in {"lora", "qlora"}:
                    return False

                if source_key == "qlora" and target_key == "quantization":
                    return True

                if source_key == "retrieval-augmented generation" and target_key == "rag":
                    return False

                return target_key not in bad_exact_targets

            if target_label == "Concept":
                return target_key not in bad_exact_targets or target_key == "vector index"

            return False

        if source_label == "Framework":
            # Milvus/Qdrant/Weaviate не USES Vector Search, они USED_FOR Vector Search.
            return False

        return False

    if rel_type == "USED_FOR":
        if target_label != "Task":
            return False

        if source_label not in {"Model", "Method", "Framework"}:
            return False

        return True

    if rel_type == "IMPLEMENTED_IN":
        if target_label != "Framework":
            return False

        if source_label not in {"Model", "Method"}:
            return False

        return True

    if rel_type == "RELATED_TO":
        if source_label not in {"Method", "Concept", "Model"}:
            return False

        if target_label not in {"Method", "Concept", "Task"}:
            return False

        if target_key in {"ner", "attention"}:
            return False

        return True

    return False


def _add(
    result: list[Relation],
    seen: set[tuple[str, str, str]],
    source: str,
    source_label: str,
    rel_type: str,
    target: str,
    target_label: str,
    evidence: str = "",
    rule: str = "rule",
    confidence: float = 0.85,
) -> None:
    source = source.strip()
    target = target.strip()

    if not source or not target:
        return

    if not _allowed_relation(source_label, rel_type, target_label, source, target):
        return

    key = (_norm_key(source), rel_type, _norm_key(target))

    if key in seen:
        return

    seen.add(key)
    result.append(
        Relation(
            from_name=source,
            from_label=source_label,
            rel_type=rel_type,
            to_name=target,
            to_label=target_label,
            evidence=evidence,
            confidence=confidence,
            rule=rule,
        )
    )


def _extract_is_a(
    sentence: str,
    items: list[dict[str, str]],
    result: list[Relation],
    seen: set[tuple[str, str, str]],
) -> None:
    markers = [
        "является моделью",
        "является методом",
        "является фреймворком",
        "is a",
        "is an",
        "is a model",
        "is a method",
        "is a framework",
        "is based on",
    ]

    if not _has_any(sentence, markers):
        return

    subject = _main_subject(items)
    if not subject:
        return

    for item in items:
        if item["name"] == subject["name"]:
            continue

        _add(
            result,
            seen,
            subject["name"],
            subject["label"],
            "IS_A",
            item["name"],
            item["label"],
            sentence,
            "strict_is_a",
            0.80,
        )


def _extract_used_for(
    sentence: str,
    items: list[dict[str, str]],
    result: list[Relation],
    seen: set[tuple[str, str, str]],
) -> None:
    markers = [
        "применяется для",
        "используется для",
        "используют для",
        "применяют для",
        "used for",
        "is used for",
        "applied for",
        "is applied for",
        "supports",
    ]

    if not _has_any(sentence, markers):
        return

    subject = _main_subject(items)
    if not subject:
        return

    for item in items:
        if item["name"] == subject["name"]:
            continue

        _add(
            result,
            seen,
            subject["name"],
            subject["label"],
            "USED_FOR",
            item["name"],
            item["label"],
            sentence,
            "strict_used_for",
            0.85,
        )


def _extract_uses(
    sentence: str,
    items: list[dict[str, str]],
    result: list[Relation],
    seen: set[tuple[str, str, str]],
) -> None:
    markers = [
        "использует",
        "используют",
        "uses",
        "use",
        "with",
        "based on",
        "опирается на",
    ]

    if not _has_any(sentence, markers):
        return

    subject = _main_subject(items)
    if not subject:
        return

    for item in items:
        if item["name"] == subject["name"]:
            continue

        _add(
            result,
            seen,
            subject["name"],
            subject["label"],
            "USES",
            item["name"],
            item["label"],
            sentence,
            "strict_uses",
            0.82,
        )


def _extract_implemented_in(
    sentence: str,
    items: list[dict[str, str]],
    result: list[Relation],
    seen: set[tuple[str, str, str]],
) -> None:
    markers = [
        "реализуется в",
        "реализован в",
        "реализована в",
        "может быть реализован в",
        "implemented in",
        "implemented with",
        "runs in",
        "served by",
        "deployed with",
    ]

    if not _has_any(sentence, markers):
        return

    subject = _main_subject(items)
    if not subject:
        return

    for item in items:
        if item["name"] == subject["name"]:
            continue

        _add(
            result,
            seen,
            subject["name"],
            subject["label"],
            "IMPLEMENTED_IN",
            item["name"],
            item["label"],
            sentence,
            "strict_implemented_in",
            0.88,
        )


def _extract_related_to(
    sentence: str,
    items: list[dict[str, str]],
    result: list[Relation],
    seen: set[tuple[str, str, str]],
) -> None:
    markers = [
        "связан с",
        "связана с",
        "связано с",
        "связывают с",
        "related to",
        "associated with",
        "connected with",
    ]

    if not _has_any(sentence, markers):
        return

    subject = _main_subject(items)
    if not subject:
        return

    for item in items:
        if item["name"] == subject["name"]:
            continue

        _add(
            result,
            seen,
            subject["name"],
            subject["label"],
            "RELATED_TO",
            item["name"],
            item["label"],
            sentence,
            "strict_related_to",
            0.78,
        )


def extract_relations(text: str, entities: list[Any]) -> list[Relation]:
    sentences = _split_sentences(text)
    result: list[Relation] = []
    seen: set[tuple[str, str, str]] = set()

    for sentence in sentences:
        items = _find_entities_in_sentence(sentence, entities)

        if len(items) < 2:
            continue

        _extract_is_a(sentence, items, result, seen)
        _extract_used_for(sentence, items, result, seen)
        _extract_uses(sentence, items, result, seen)
        _extract_implemented_in(sentence, items, result, seen)
        _extract_related_to(sentence, items, result, seen)

    return result
