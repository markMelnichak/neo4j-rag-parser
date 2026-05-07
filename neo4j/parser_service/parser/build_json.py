from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List

from parser.entity_extractor import ExtractedEntity
from parser.relation_extractor import ExtractedRelation


def build_graph_payload(
    entities: List[ExtractedEntity],
    relations: List[ExtractedRelation],
    source_name: str,
) -> dict:
    nodes = {}
    for entity in entities:
        key = (entity.label, entity.canonical)
        if key not in nodes:
            nodes[key] = {
                "label": entity.label,
                "name": entity.canonical,
                "normalized_name": entity.canonical.lower(),
                "aliases": [],
                "source": source_name,
                "description": None,
            }

    payload = {
        "source": source_name,
        "nodes": list(nodes.values()),
        "relations": [
            {
                "from_name": rel.from_name,
                "from_label": rel.from_label,
                "type": rel.rel_type,
                "to_name": rel.to_name,
                "to_label": rel.to_label,
                "evidence": rel.evidence,
                "confidence": rel.confidence,
                "rule": rel.rule,
                "source": source_name,
            }
            for rel in relations
        ],
    }
    return payload


def save_payload(payload: dict, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
