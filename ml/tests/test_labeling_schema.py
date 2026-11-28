"""Stream B: pins labeling CSV headers documented in labeling/SCHEMA.md (C6 for labels.csv)."""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _header(rel: str) -> list[str]:
    with open(ROOT / rel, newline="") as f:
        return next(csv.reader(f))


def test_manifest_header():
    assert _header("labeling/queries/manifest.csv") == [
        "photo_id", "object_id", "filename", "description", "category", "split", "query_box", "is_demo_object"]


def test_candidates_header():
    assert _header("labeling/candidates.csv") == [
        "photo_id", "candidate_pos", "title", "link", "source", "price", "rating", "review_count",
        "image_url", "thumbnail_url", "local_image_path", "image_kind"]


def test_labels_header_c6():
    assert _header("labeling/labels.csv") == [
        "photo_id", "candidate_pos", "candidate_link", "candidate_image", "label", "labeler"]
