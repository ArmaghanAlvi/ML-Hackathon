"""make_pairs.py

Owner: Stream A · Roadmap: Stage 2d / 3c
Purpose: Build positive pairs (same parent_asin) and random negatives per split; add hard negatives (zero-shot SigLIP neighbours, train split only) after 3c.

Inputs:  ml/data/splits/{train,val,test}.parquet, optionally ml/data/embeddings/ for hard negatives
Outputs: ml/data/pairs/{train,val,test}.parquet (img_a, img_b, label, kind)

STUB: not implemented yet.
"""
from __future__ import annotations

import argparse


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--splits-dir", default='ml/data/splits', help="Splits dir")
    parser.add_argument("--hard-negatives", action="store_true", help="Mine hard negatives (train only)")
    parser.add_argument("--out-dir", default='ml/data/pairs', help="Output dir")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    parse_args(argv)
    raise NotImplementedError("TODO: Stage 2d / 3c (make_pairs)")


if __name__ == "__main__":
    main()
