"""embed.py

Owner: Stream A · Roadmap: Stage 3a
Purpose: Compute frozen ResNet-50 and SigLIP 2 embeddings for every image, plus 2-4 augmented views of each TRAIN image.

Inputs:  ml/data/splits/*.parquet, ml/data/images/
Outputs: ml/data/embeddings/<backbone>_<split>.npy + index parquet

STUB: dataset-wide extraction and SigLIP 2 are pending.
"""
from __future__ import annotations

import argparse
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PIL.Image import Image
    from torch import Tensor


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--backbone", choices=['resnet50','siglip2'], required=True, help="Backbone")
    parser.add_argument("--augment", type=int, default=0, help="Augmented views per train image")
    parser.add_argument("--out-dir", default='ml/data/embeddings', help="Output dir")
    parser.add_argument("--image", help="Image path for a one-image smoke test")
    return parser.parse_args(argv)


def load_resnet50():
    from torch import nn
    from torchvision.models import ResNet50_Weights, resnet50

    weights = ResNet50_Weights.IMAGENET1K_V2
    model = resnet50(weights=weights)
    model.fc = nn.Identity()
    return model.eval(), weights.transforms()


def embed_images(images: list[Image], backbone: str) -> Tensor:
    """Return one L2-normalized embedding per image, in input order."""
    if backbone != "resnet50":
        raise NotImplementedError(f"Embedding extraction for {backbone!r} is not implemented")
    if not images:
        raise ValueError("Pass at least one image")

    import torch
    from torch.nn import functional as F

    model, preprocess = load_resnet50()
    batch = torch.stack([preprocess(image.convert("RGB")) for image in images])

    with torch.no_grad():
        return F.normalize(model(batch), p=2, dim=1)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)

    if args.backbone == "resnet50" and args.image is not None:
        from PIL import Image

        with Image.open(args.image) as image:
            embeddings = embed_images([image], args.backbone)
        print(embeddings.shape)
        return

    raise NotImplementedError("TODO: Stage 3a (embed)")


if __name__ == "__main__":
    main()
