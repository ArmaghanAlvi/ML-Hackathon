"""eval_offline.py

Owner: Stream A · Roadmap: Stage 3f
Purpose: One-time TEST evaluation after the model is frozen: Recall@K for ResNet / zero-shot SigLIP / trained head, PR curve, ROC-AUC.

Inputs:  ml/data/splits/test.parquet, ml/data/embeddings/, frozen head weights, ml/artifacts/thresholds.json
Outputs: ml/artifacts/metrics/offline.json, ml/artifacts/figures/{recall_at_k,pr_curve,roc}.png

STUB: not implemented yet.
"""
from __future__ import annotations

import argparse


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--split", default='test', help="Split to evaluate (test runs ONCE)")
    parser.add_argument("--out-dir", default='ml/artifacts', help="Artifacts dir")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    parse_args(argv)
    raise NotImplementedError("TODO: Stage 3f (eval_offline)")


if __name__ == "__main__":
    main()
