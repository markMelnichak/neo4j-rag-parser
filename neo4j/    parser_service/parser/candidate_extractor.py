from __future__ import annotations

import re
from typing import Dict, List, Set

from parser.entity_extractor import ExtractedEntity


BLACKLIST = {
    "model", "models", "concept", "concepts", "task", "tasks", "method", "methods",
    "framework", "frameworks", "image", "text", "speech", "generation",
    "recognition", "translation", "question", "answering", "feature",
    "space", "audio", "net", "network", "neural", "face", "hugging",
    "transformers", "diffusion", "guidance", "classifier-free",
    "машинный", "перевод", "вопрос", "ответ", "метод", "методы",
    "модель", "модели", "задача", "задачи", "фреймворк", "концепт"
}

COMMON_SINGLE_WORDS = {
    "This", "That", "These", "Those", "Such", "When", "Where", "What", "Why",
    "The", "A", "An", "If", "For", "In", "On", "And", "Or", "But",
    "Этот", "Эта", "Эти", "Такой", "Такая", "Также", "Кроме", "Если", "При",
    "Во", "В", "На", "И", "Но", "Для"
}

# Только multiword technical phrases
MULTIWORD_PATTERN = re.compile(
    r'\b(?:[A-ZА-Я][A-Za-zА-Яа-я0-9]*(?:-[A-Za-zА-Яа-я0-9]+)*)(?:\s+(?:[A-ZА-Я][A-Za-zА-Яа-я0-9]*(?:-[A-Za-zА-Яа-я0-9]+)*)){1,4}\b'
)

# Только сильные single-word technical forms
STRONG_SINGLE_PATTERN = re.compile(
    r'\b(?:[A-Z]{2,}[A-Za-z0-9-]*|[A-Z][A-Za-z0-9]+-[A-Za-z0-9]+)\b'
)


def _build_known_mentions(config: dict, known_entities: List[ExtractedEntity]) -> Set[str]:
    known: Set[str] = set()

    for label_values in config.get("entities", {}).values():
        for value in label_values:
            known.add(value.lower())

    for alias in config.get("aliases", {}).keys():
        known.add(alias.lower())

    for entity in known_entities:
        known.add(entity.text.lower())
        known.add(entity.canonical.lower())

    return known


def _build_known_parts(known_mentions: Set[str]) -> Set[str]:
    parts: Set[str] = set()
    for item in known_mentions:
        for part in re.split(r"[\s\-]+", item):
            part = part.strip().lower()
            if part:
                parts.add(part)
    return parts


def _normalize_candidate(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip(" .,:;!?()[]{}\"'").strip()


def _is_good_candidate(text: str, known_mentions: Set[str], known_parts: Set[str]) -> bool:
    if not text:
        return False

    low = text.lower()

    if low in known_mentions:
        return False

    if low in COMMON_SINGLE_WORDS:
        return False

    if low in BLACKLIST:
        return False

    if len(text) <= 2:
        return False

    # Если это одно слово и оно является частью уже известной многословной сущности — отбрасываем
    if " " not in text and "-" not in text and low in known_parts:
        return False

    # Одно слово разрешаем только если это реально сильный технический формат
    if " " not in text and "-" not in text:
        if not re.fullmatch(r"(?:[A-Z]{2,}[A-Za-z0-9]*|[A-Z][A-Za-z0-9]{2,})", text):
            return False

    return True


def extract_candidate_strings(sentence: str, known_mentions: Set[str]) -> List[str]:
    known_parts = _build_known_parts(known_mentions)
    candidates: List[str] = []

    # Сначала multiword
    for match in MULTIWORD_PATTERN.finditer(sentence):
        value = _normalize_candidate(match.group(0))
        if _is_good_candidate(value, known_mentions, known_parts):
            candidates.append(value)

    # Потом только сильные single-word формы
    for match in STRONG_SINGLE_PATTERN.finditer(sentence):
        value = _normalize_candidate(match.group(0))
        if _is_good_candidate(value, known_mentions, known_parts):
            candidates.append(value)

    unique = []
    seen = set()
    for c in candidates:
        key = c.lower()
        if key in seen:
            continue
        seen.add(key)
        unique.append(c)

    return unique


def extract_candidate_entities(
    entities_by_sentence: Dict[str, List[ExtractedEntity]],
    config: dict,
) -> List[ExtractedEntity]:
    from parser.entity_classifier import classify_candidate

    known_entities = [e for values in entities_by_sentence.values() for e in values]
    known_mentions = _build_known_mentions(config, known_entities)

    results: List[ExtractedEntity] = []

    for sentence, sent_entities in entities_by_sentence.items():
        candidate_strings = extract_candidate_strings(sentence, known_mentions)

        for candidate in candidate_strings:
            label, canonical = classify_candidate(candidate, sentence)
            if label is None:
                continue

            results.append(
                ExtractedEntity(
                    text=candidate,
                    label=label,
                    canonical=canonical,
                    normalized_name=canonical.lower(),
                    sentence=sentence,
                )
            )

    unique = {}
    for item in results:
        key = (item.canonical, item.label, item.sentence)
        unique[key] = item

    return list(unique.values())
