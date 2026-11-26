"""train_reviews.py

Owner: Stream B · Roadmap: Stage 7b / 7c
Purpose: TF-IDF + logistic regression baseline (vectorizer fit on TRAIN only) and DistilBERT fine-tune (1-2 epochs, Colab).

Inputs:  ml/data/reviews/{train,val}.parquet
Outputs: model pushed to HF Hub, ml/artifacts/metrics/reviews.json (macro-F1, PR-AUC)

STUB: not implemented yet.
"""
from __future__ import annotations

import argparse


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--model", choices=['tfidf','distilbert'], default='tfidf', help="Model")
    parser.add_argument("--epochs", type=int, default=1, help="Epochs (DistilBERT)")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    parse_args(argv)
    raise NotImplementedError("TODO: Stage 7b / 7c (train_reviews)")


if __name__ == "__main__":
    main()
