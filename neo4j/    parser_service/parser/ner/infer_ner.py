from __future__ import annotations

import argparse
from pathlib import Path

import spacy


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="parser/models/ner_model")
    parser.add_argument("--text", required=True)
    args = parser.parse_args()

    nlp = spacy.load(args.model)
    doc = nlp(args.text)

    for ent in doc.ents:
        print(f"{ent.text} | {ent.label_} | {ent.start_char}:{ent.end_char}")


if __name__ == "__main__":
    main()
