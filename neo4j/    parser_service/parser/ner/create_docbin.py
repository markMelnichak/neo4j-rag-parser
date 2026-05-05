from __future__ import annotations

from pathlib import Path
import random

import spacy
from spacy.tokens import DocBin

from parser.ner.training_data import TRAIN_DATA


def main() -> None:
    random.seed(42)
    data = TRAIN_DATA[:]
    random.shuffle(data)

    split_idx = max(1, int(len(data) * 0.8))
    train_data = data[:split_idx]
    dev_data = data[split_idx:]

    nlp = spacy.blank("xx")

    out_dir = Path("parser/ner/data")
    out_dir.mkdir(parents=True, exist_ok=True)

    for dataset, name in [(train_data, "train"), (dev_data, "dev")]:
        db = DocBin()
        for text, annot in dataset:
            doc = nlp.make_doc(text)
            ents = []
            for start, end, label in annot["entities"]:
                span = doc.char_span(start, end, label=label, alignment_mode="contract")
                if span is None:
                    continue
                ents.append(span)
            doc.ents = ents
            db.add(doc)
        db.to_disk(out_dir / f"{name}.spacy")

    print("DocBin created:")
    print(out_dir / "train.spacy")
    print(out_dir / "dev.spacy")


if __name__ == "__main__":
    main()
