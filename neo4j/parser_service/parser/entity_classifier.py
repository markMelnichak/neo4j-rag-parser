from __future__ import annotations

import re
from typing import Optional, Tuple


TASK_HINTS = [
    "classification", "translation", "recognition", "segmentation",
    "generation", "summarization", "answering"
]

METHOD_HINTS = [
    "tuning", "optimization", "guidance", "extraction",
    "lora", "rlhf", "dropout", "backpropagation"
]

FRAMEWORK_HINTS = [
    "pytorch", "tensorflow", "keras", "transformers"
]

CONCEPT_HINTS = [
    "space", "map", "embedding", "network", "attention", "model"
]


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def classify_candidate(candidate: str, sentence: str) -> Tuple[Optional[str], Optional[str]]:
    cand = _norm(candidate)
    low = cand.lower()
    sent = sentence.lower()

    # Framework
    if any(h in low for h in FRAMEWORK_HINTS):
        return "Framework", cand

    if re.search(rf"\b{re.escape(low)}\b", sent) and (
        "implemented in" in sent
        or "реализуется в" in sent
        or "реализован в" in sent
        or "разворачивается через" in sent
    ):
        return "Framework", cand

    # Method
    if any(h in low for h in METHOD_HINTS):
        return "Method", cand

    if re.search(rf"\b{re.escape(low)}\b", sent) and (
        "uses" in sent
        or "использует" in sent
        or "может использовать" in sent
        or "часто использует" in sent
    ):
        return "Method", cand

    # Task
    if any(h in low for h in TASK_HINTS):
        return "Task", cand

    if re.search(rf"\b{re.escape(low)}\b", sent) and (
        "used for" in sent
        or "используется для" in sent
        or "применяется для" in sent
    ):
        return "Task", cand

    # Model
    if re.search(rf"\b{re.escape(low)}\b", sent) and (
        "is a" in sent
        or "является моделью" in sent
        or "представляет собой модель" in sent
        or "относится к классу" in sent
        or "относится к типу" in sent
    ):
        return "Model", cand

    # lexical model hints for many AI names
    if re.match(r"^(?:[A-Z]{2,}[A-Za-z0-9-]*|[A-Z][A-Za-z0-9]+(?:-[A-Za-z0-9]+)*)$", cand):
        if low not in {"transformer", "network", "model"}:
            return "Model", cand

    # Concept
    if any(h in low for h in CONCEPT_HINTS):
        return "Concept", cand

    if re.search(rf"\b{re.escape(low)}\b", sent) and (
        "связано с" in sent
        or "связан с" in sent
        or "related to" in sent
    ):
        return "Concept", cand

    return None, None
