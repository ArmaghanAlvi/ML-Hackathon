"""dedupe.py

Owner: Stream A · Roadmap: Stage 2c
Purpose: Find duplicate/near-duplicate images across products with perceptual hashes (imagehash) and group them. Runs BEFORE splitting.

Inputs:  ml/data/catalog.parquet, ml/data/images/
Outputs: ml/data/dedupe_groups.parquet (image_id -> dup_group_id), ml/artifacts/metrics/dedupe.json (counts)

STUB: not implemented yet.
"""
from __future__ import annotations

import argparse


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--catalog", default='ml/data/catalog.parquet', help="Catalog")
    parser.add_argument("--hamming", type=int, default=4, help="Max pHash Hamming distance for a duplicate")
    parser.add_argument("--out", default='ml/data/dedupe_groups.parquet', help="Output groups")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    parse_args(argv)
    raise NotImplementedError("TODO: Stage 2c (dedupe)")


if __name__ == "__main__":
    main()
