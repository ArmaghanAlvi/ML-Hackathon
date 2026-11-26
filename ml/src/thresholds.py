"""thresholds.py

Owner: Stream A · Roadmap: Stage 3e
Purpose: Pick identical/similar score cutoffs on VALIDATION (never test).

Inputs:  val scores from the frozen matcher, ml/data/pairs/val.parquet
Outputs: ml/artifacts/thresholds.json ({'identical': float, 'similar': float}, contract C5)

STUB: not implemented yet.
"""
from __future__ import annotations

import argparse


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--pairs", default='ml/data/pairs/val.parquet', help="Validation pairs")
    parser.add_argument("--out", default='ml/artifacts/thresholds.json', help="Output thresholds")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    parse_args(argv)
    raise NotImplementedError("TODO: Stage 3e (thresholds)")


if __name__ == "__main__":
    main()
