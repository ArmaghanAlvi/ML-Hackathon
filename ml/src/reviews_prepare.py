"""reviews_prepare.py

Owner: Stream B · Roadmap: Stage 7a
Purpose: Sample ~50k reviews from our categories; helpful = >=3 votes, not helpful = 0 votes on old-enough reviews; split BY PRODUCT.

Inputs:  Amazon Reviews 2023 reviews for categories in docs/decisions.md
Outputs: ml/data/reviews/{train,val,test}.parquet (text, label, parent_asin)

STUB: not implemented yet.
"""
from __future__ import annotations

import argparse


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--n", type=int, default=50000, help="Number of reviews")
    parser.add_argument("--out-dir", default='ml/data/reviews', help="Output dir")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    parse_args(argv)
    raise NotImplementedError("TODO: Stage 7a (reviews_prepare)")


if __name__ == "__main__":
    main()
