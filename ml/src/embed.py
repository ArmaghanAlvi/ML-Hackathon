"""embed.py

Owner: Stream A · Roadmap: Stage 3a
Purpose: Compute frozen ResNet-50 and SigLIP 2 embeddings for every image, plus 2-4 augmented views of each TRAIN image.

Inputs:  ml/data/splits/*.parquet, ml/data/images/
Outputs: ml/data/embeddings/<backbone>_<split>.npy + index parquet

STUB: not implemented yet.
"""
from __future__ import annotations

import argparse


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--backbone", choices=['resnet50','siglip2'], required=True, help="Backbone")
    parser.add_argument("--augment", type=int, default=0, help="Augmented views per train image")
    parser.add_argument("--out-dir", default='ml/data/embeddings', help="Output dir")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    parse_args(argv)
    raise NotImplementedError("TODO: Stage 3a (embed)")


if __name__ == "__main__":
    main()
