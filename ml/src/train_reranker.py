"""train_reranker.py

Owner: Stream A · Roadmap: Stage 8b / 8c
Purpose: XGBoost rank:pairwise re-ranker on labeled real-photo candidates, cross-validation GROUPED BY PHOTO.

Inputs:  labeling/labels.csv, per-candidate features (matcher/ResNet/zero-shot scores, Lens position, title similarity, relative price)
Outputs: ml/artifacts/metrics/reranker.json (NDCG@3, precision@3 per fold), local model file (gitignored)

STUB: not implemented yet.
"""
from __future__ import annotations

import argparse


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--labels", default='labeling/labels.csv', help="Labels CSV")
    parser.add_argument("--folds", type=int, default=5, help="Grouped CV folds")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    parse_args(argv)
    raise NotImplementedError("TODO: Stage 8b / 8c (train_reranker)")


if __name__ == "__main__":
    main()
