"""make_splits.py

Owner: Stream A · Roadmap: Stage 2c
Purpose: Split 70/15/15 by parent_asin so no product and no duplicate group crosses splits; verify zero overlap.

Inputs:  ml/data/catalog.parquet, ml/data/dedupe_groups.parquet
Outputs: ml/data/splits/{train,val,test}.parquet (split by parent_asin)

STUB: not implemented yet.
"""
from __future__ import annotations

import argparse


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--catalog", default='ml/data/catalog.parquet', help="Catalog")
    parser.add_argument("--groups", default='ml/data/dedupe_groups.parquet', help="Dedupe groups")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--out-dir", default='ml/data/splits', help="Output dir")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    parse_args(argv)
    raise NotImplementedError("TODO: Stage 2c (make_splits)")


if __name__ == "__main__":
    main()
