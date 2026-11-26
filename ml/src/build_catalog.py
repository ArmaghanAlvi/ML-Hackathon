"""build_catalog.py

Owner: Stream A · Roadmap: Stage 2a / 2b
Purpose: Filter chosen categories to products with >=2 images and a title, sample ~5-10k products, download images (~384px, polite rate, resumable).

Inputs:  Amazon Reviews 2023 metadata for categories in docs/decisions.md
Outputs: ml/data/catalog.parquet (one row per image: parent_asin, image_id, title, category, path), ml/data/images/<parent_asin>/<image_id>.jpg

STUB: not implemented yet.
"""
from __future__ import annotations

import argparse


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--categories", nargs='+', help="Categories to include")
    parser.add_argument("--max-products", type=int, default=10000, help="Sample size")
    parser.add_argument("--out", default='ml/data/catalog.parquet', help="Output catalog")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    parse_args(argv)
    raise NotImplementedError("TODO: Stage 2a / 2b (build_catalog)")


if __name__ == "__main__":
    main()
