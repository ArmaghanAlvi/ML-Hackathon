"""eval_live.py

Owner: Stream B · Roadmap: Stage 6e
Purpose: Live evaluation on the real-photo TEST photos: precision@3 (identical), 3-class confusion matrix, comparison of Lens order vs. ResNet vs. zero-shot SigLIP vs. our matcher.

Inputs:  labeling/labels.csv, labeling/queries/manifest.csv (split=test), labeling/lens_cache/<photo_id>.json
Outputs: ml/artifacts/metrics/live.json, ml/artifacts/figures/{live_comparison,confusion_matrix}.png

STUB: not implemented yet.
"""
from __future__ import annotations

import argparse


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--labels", default='labeling/labels.csv', help="Labels CSV")
    parser.add_argument("--manifest", default='labeling/queries/manifest.csv', help="Photo manifest")
    parser.add_argument("--split", choices=['calibration','test'], default='test', help="Photo split")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    parse_args(argv)
    raise NotImplementedError("TODO: Stage 6e (eval_live)")


if __name__ == "__main__":
    main()
