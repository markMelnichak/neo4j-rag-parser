from __future__ import annotations

import argparse
from pathlib import Path

from parser.build_json import build_graph_payload, save_payload
from parser.entity_extractor import (
    build_nlp,
    extract_entities,
    group_entities_by_sentence,
    load_entity_config,
)
from parser.extract_text import extract_text_from_supported_file
from parser.import_to_neo4j import Neo4jImporter, load_neo4j_config
from parser.normalize import normalize_text
from parser.relation_extractor import extract_relations
from parser.entity_validator import validate_entities, validate_relations


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="PDF/TXT/MD -> intermediate TXT/MD -> entities/relations -> JSON -> Neo4j"
    )
    parser.add_argument("--input", required=True, help="Path to input file (.pdf, .txt, .md)")
    parser.add_argument("--output-dir", default="parser/output", help="Directory for intermediate/output files")
    parser.add_argument("--config", default="parser/config/entity_dict.json", help="Path to entity dictionary config")
    parser.add_argument("--import-neo4j", action="store_true", help="Import extracted graph payload into Neo4j")
    parser.add_argument("--use-ner", action="store_true", help="Use trained spaCy NER model")
    parser.add_argument("--ner-model", default="parser/models/ner_model", help="Path to trained spaCy NER model")
    return parser.parse_args()


def _dedupe_entities(entities):
    unique = {}
    for e in entities:
        key = (e.canonical, e.label, e.sentence)
        unique[key] = e
    return list(unique.values())


def main() -> None:
    args = parse_args()

    input_path = Path(args.input).resolve()
    output_dir = Path(args.output_dir).resolve()
    config_path = Path(args.config).resolve()

    print("[1/6] Extracting input to intermediate TXT/MD...")
    raw_text, txt_path, md_path = extract_text_from_supported_file(input_path, output_dir)

    print(f"  TXT: {txt_path}")
    print(f"  MD : {md_path}")

    print("[2/6] Normalizing text...")
    normalized_text = normalize_text(raw_text)

    normalized_txt_path = output_dir / f"{input_path.stem}.normalized.txt"
    normalized_txt_path.write_text(normalized_text, encoding="utf-8")
    print(f"  NORMALIZED TXT: {normalized_txt_path}")

    print("[3/6] Loading entity config and building dictionary NLP pipeline...")
    config = load_entity_config(config_path)
    nlp = build_nlp(config)

    print("[4/6] Extracting dictionary entities...")
    dict_entities = extract_entities(normalized_text, nlp)
    print(f"  Dictionary entities found: {len(dict_entities)}")

    all_entities = list(dict_entities)

    if args.use_ner:
        print("[4.1/6] Extracting entities with trained spaCy NER...")
        from parser.ner.merge_ner_entities import extract_entities_with_trained_ner
        ner_entities = extract_entities_with_trained_ner(normalized_text, args.ner_model)
        print(f"  NER entities found: {len(ner_entities)}")
        all_entities.extend(ner_entities)
    else:
        print("[4.1/6] spaCy NER disabled")

    entities = _dedupe_entities(all_entities)
    print(f"  Total entities after merge: {len(entities)}")

    for e in entities:
        print(f"  ENTITY | label={e.label} | text={e.text} | canonical={e.canonical}")

    print("[4.2/6] Validating entities...")
    entities = validate_entities(entities)

    print("[5/6] Extracting relations...")
    sentence_entities = group_entities_by_sentence(entities)
    relations = extract_relations(normalized_text, entities)
    print(f"  Relations found: {len(relations)}")
    for r in relations:
        print(f"  REL | {r.from_name} -[{r.rel_type}]-> {r.to_name}")

    print("[5.1/6] Validating relations...")
    relations = validate_relations(relations, entities)

    print("[6/6] Building JSON payload...")
    payload = build_graph_payload(
        entities=entities,
        relations=relations,
        source_name=input_path.name,
    )

    payload_path = output_dir / f"{input_path.stem}.graph.json"
    save_payload(payload, payload_path)
    print(f"  JSON: {payload_path}")

    if args.import_neo4j:
        print("[Neo4j] Importing payload into database...")
        config_neo4j = load_neo4j_config()
        with Neo4jImporter(config_neo4j) as importer:
            importer.import_payload(payload)
        print("[Neo4j] Import finished.")

    print("Done.")


if __name__ == "__main__":
    main()
