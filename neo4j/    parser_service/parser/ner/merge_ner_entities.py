from __future__ import annotations

from typing import List

import spacy

from parser.entity_extractor import ExtractedEntity


LABEL_MAP = {
    "MODEL": "Model",
    "TASK": "Task",
    "METHOD": "Method",
    "FRAMEWORK": "Framework",
    "CONCEPT": "Concept",
}


def _get_sentence_text(doc, ent) -> str:
    if doc.has_annotation("SENT_START"):
        for sent in doc.sents:
            if ent.start >= sent.start and ent.end <= sent.end:
                return sent.text.strip()

    start = max(0, ent.start_char - 120)
    end = min(len(doc.text), ent.end_char + 120)
    return doc.text[start:end].strip()


def extract_entities_with_trained_ner(text: str, model_path: str) -> List[ExtractedEntity]:
    nlp = spacy.load(model_path)

    if "sentencizer" not in nlp.pipe_names:
        nlp.add_pipe("sentencizer", first=True)

    doc = nlp(text)

    results = []
    for ent in doc.ents:
        label = LABEL_MAP.get(ent.label_)
        if not label:
            continue

        sent_text = _get_sentence_text(doc, ent)

        results.append(
            ExtractedEntity(
                text=ent.text,
                label=label,
                canonical=ent.text.strip(),
                normalized_name=ent.text.strip().lower(),
                sentence=sent_text,
            )
        )

    unique = {}
    for item in results:
        key = (item.canonical, item.label, item.sentence)
        unique[key] = item

    return list(unique.values())
