from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import spacy
from spacy.language import Language


@dataclass
class ExtractedEntity:
    text: str
    label: str
    canonical: str
    normalized_name: str
    sentence: str


def load_entity_config(config_path: Path) -> dict:
    return json.loads(config_path.read_text(encoding="utf-8"))


def build_nlp(config: dict) -> Language:
    nlp = spacy.blank("en")
    nlp.add_pipe("sentencizer")

    ruler = nlp.add_pipe(
        "entity_ruler",
        config={
            "overwrite_ents": True,
            "phrase_matcher_attr": "LOWER"
        }
    )

    patterns = []

    for label, values in config["entities"].items():
        for value in values:
            patterns.append(
                {
                    "label": label,
                    "pattern": value,
                    "id": value
                }
            )

    for alias, meta in config.get("aliases", {}).items():
        patterns.append(
            {
                "label": meta["label"],
                "pattern": alias,
                "id": meta["canonical"]
            }
        )

    ruler.add_patterns(patterns)
    return nlp


def extract_entities(text: str, nlp: Language) -> List[ExtractedEntity]:
    doc = nlp(text)
    result: List[ExtractedEntity] = []

    for sent in doc.sents:
        sent_text = sent.text.strip()
        if not sent_text:
            continue

        for ent in sent.ents:
            canonical = ent.ent_id_ if ent.ent_id_ else ent.text
            result.append(
                ExtractedEntity(
                    text=ent.text,
                    label=ent.label_,
                    canonical=canonical,
                    normalized_name=canonical.lower(),
                    sentence=sent_text,
                )
            )

    unique = {}
    for item in result:
        key = (item.canonical, item.label, item.sentence)
        unique[key] = item

    return list(unique.values())


def group_entities_by_sentence(
    entities: List[ExtractedEntity],
) -> Dict[str, List[ExtractedEntity]]:
    grouped: Dict[str, List[ExtractedEntity]] = {}
    for entity in entities:
        grouped.setdefault(entity.sentence, []).append(entity)
    return grouped
