"""train_head.py

Owner: Stream A · Roadmap: Stage 3d
Purpose: Train an MLP projection head (InfoNCE or triplet loss) on frozen embeddings; grid search on VALIDATION only.

Inputs:  ml/data/embeddings/, ml/data/pairs/{train,val}.parquet
Outputs: head weights (pushed to HF Hub repo in docs/decisions.md, never git), ml/artifacts/metrics/train_head.json

STUB: not implemented yet.
"""
from __future__ import annotations

import argparse


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--loss", choices=['infonce','triplet'], default='infonce', help="Loss")
    parser.add_argument("--epochs", type=int, default=10, help="Epochs")
    parser.add_argument("--out-dir", default='ml/data/weights', help="Local weights dir (gitignored)")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    parse_args(argv)
    raise NotImplementedError("TODO: Stage 3d (train_head)")


if __name__ == "__main__":
    main()
