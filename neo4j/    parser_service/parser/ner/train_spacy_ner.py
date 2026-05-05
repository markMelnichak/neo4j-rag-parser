from __future__ import annotations

from pathlib import Path
import random

import spacy
from spacy.training import Example
from spacy.tokens import DocBin
from spacy.util import minibatch, compounding


LABELS = ["MODEL", "TASK", "METHOD", "FRAMEWORK", "CONCEPT"]


def load_examples(nlp, path: Path):
    db = DocBin().from_disk(path)
    docs = list(db.get_docs(nlp.vocab))
    examples = []
    for doc in docs:
        examples.append(
            Example.from_dict(
                nlp.make_doc(doc.text),
                {"entities": [(ent.start_char, ent.end_char, ent.label_) for ent in doc.ents]},
            )
        )
    return examples


def main() -> None:
    random.seed(42)

    train_path = Path("parser/ner/data/train.spacy")
    dev_path = Path("parser/ner/data/dev.spacy")
    out_dir = Path("parser/models/ner_model")

    nlp = spacy.blank("xx")

    if "sentencizer" not in nlp.pipe_names:
        nlp.add_pipe("sentencizer", first=True)

    if "ner" not in nlp.pipe_names:
        ner = nlp.add_pipe("ner", last=True)
    else:
        ner = nlp.get_pipe("ner")

    for label in LABELS:
        ner.add_label(label)

    train_examples = load_examples(nlp, train_path)
    dev_examples = load_examples(nlp, dev_path)

    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "ner"]
    with nlp.disable_pipes(*other_pipes):
        optimizer = nlp.begin_training()

        for epoch in range(30):
            random.shuffle(train_examples)
            losses = {}
            batches = minibatch(train_examples, size=compounding(2.0, 8.0, 1.5))
            for batch in batches:
                nlp.update(batch, sgd=optimizer, losses=losses, drop=0.15)

            print(f"epoch={epoch+1} losses={losses}")

    out_dir.mkdir(parents=True, exist_ok=True)
    nlp.to_disk(out_dir)
    print(f"Model saved to: {out_dir}")


if __name__ == "__main__":
    main()
