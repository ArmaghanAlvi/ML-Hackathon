"""Stream B: offline tests for `reviews_prepare.py scan` (TICKET-B03). Local files only, never the network."""
from __future__ import annotations

import gzip
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

pa = pytest.importorskip("pyarrow")
import pyarrow.parquet as pq  # noqa: E402

from ml.src import reviews_prepare as rp  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
VOTES = [0, 1, 2, 3, 7, 60]
MARCH_2019_MS = int(datetime(2019, 3, 10, tzinfo=timezone.utc).timestamp() * 1000)
JULY_2021_MS = int(datetime(2021, 7, 20, tzinfo=timezone.utc).timestamp() * 1000)
N_VALID = 36
SECONDS_ROW = 5      # this row's timestamp is in seconds
NULL_TEXT_ROW = 0    # text is null (row_idx 0, so it lands in every thin sample)


def toy_lines() -> list[str]:
    """36 valid rows (votes cycle 0,1,2,3,7,60; rows 0-19 in 2019-03, 20-35 in 2021-07), plus 2 malformed lines
    (bad JSON, missing helpful_vote) and one blank line, which is skipped and not counted."""
    lines = []
    for i in range(N_VALID):
        ts = (MARCH_2019_MS if i < 20 else JULY_2021_MS) + i * 1000
        if i == SECONDS_ROW:
            ts //= 1000
        rec = {
            "rating": float(i % 5 + 1), "title": f"title {i}",
            "text": None if i == NULL_TEXT_ROW else "word " * (i + 1),
            "images": [{"url": "x"}] * (i % 3), "asin": f"A{i}", "parent_asin": f"P{i % 7}",
            "user_id": f"U{i}", "timestamp": ts, "helpful_vote": VOTES[i % 6], "verified_purchase": i % 2 == 0,
        }
        lines.append(json.dumps(rec))
        if i == 10:
            lines.append('{"rating": 5.0, "text": "broken"')            # bad JSON
            lines.append(json.dumps({"timestamp": MARCH_2019_MS, "text": "no votes field"}))
            lines.append("")
    return lines


def write_gz(path: Path, lines: list[str]) -> Path:
    with gzip.open(path, "wt", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return path


def write_plain(path: Path, lines: list[str]) -> Path:
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def run(tmp_path: Path, src: Path, *extra: str, out: str = "out", category: str = "Toy"):
    out_dir = tmp_path / out
    code = rp.main(["scan", "--category", category, "--input", str(src), "--out", str(out_dir), *extra])
    summary_path = out_dir / f"{category}_summary.json"
    summary = json.loads(summary_path.read_text()) if summary_path.exists() else None
    return code, summary, out_dir


@pytest.fixture
def toy_gz(tmp_path: Path) -> Path:
    return write_gz(tmp_path / "Toy.jsonl.gz", toy_lines())


# 1. exact aggregates -----------------------------------------------------------------------------------------

def test_aggregates_match_hand_counts(tmp_path, toy_gz):
    code, s, out = run(tmp_path, toy_gz, "--checkpoint-every", "5")
    assert code == 0
    assert s["completed"] is True and s["error"] is None
    assert s["source"] == str(toy_gz)
    assert s["n_rows"] == 36
    assert s["n_malformed"] == 2
    assert s["ts_unit_counts"] == {"ms": 35, "s": 1}

    hist = s["helpful_vote_hist"]
    assert list(hist) == [str(k) for k in range(50)] + ["50+"]
    assert {k: v for k, v in hist.items() if v} == {"0": 6, "1": 6, "2": 6, "3": 6, "7": 6, "50+": 6}

    assert s["months"] == {
        "2019-03": {"n": 20, "v0": 4, "v1": 4, "v2": 3, "v3plus": 9, "v5plus": 6, "v10plus": 3},
        "2021-07": {"n": 16, "v0": 2, "v1": 2, "v2": 3, "v3plus": 9, "v5plus": 6, "v10plus": 3},
    }
    assert s["rating_hist"] == {"1": 8, "2": 7, "3": 7, "4": 7, "5": 7}
    assert s["n_verified"] == 18
    assert s["ts_min_ms"] == MARCH_2019_MS
    assert s["ts_max_ms"] == JULY_2021_MS + 35_000
    assert s["texts_seen"] == {"pos2": 24, "zero": 6}  # votes 2, 3, 7, 60 vs. 0; 1-vote rows are skipped
    assert not list(out.glob("*.tmp"))  # checkpoints replaced their temp files


# 2 + 4. thin sample ---------------------------------------------------------------------------------------------

def test_thin_sample_every_kth_row(tmp_path, toy_gz):
    code, s, out = run(tmp_path, toy_gz, "--thin-every", "3")
    assert code == 0
    table = pq.read_table(out / "Toy_thin.parquet")
    assert table.column("row_idx").to_pylist() == list(range(0, 36, 3))
    assert s["n_thin"] == 12
    assert dict(zip(table.schema.names, map(str, table.schema.types))) == {
        "row_idx": "int64", "parent_asin": "string", "timestamp_ms": "int64", "helpful_vote": "int32",
        "rating": "float", "verified_purchase": "bool", "word_count": "int32", "n_images": "int16"}
    rows = table.to_pylist()
    assert rows[1] == {"row_idx": 3, "parent_asin": "P3", "timestamp_ms": MARCH_2019_MS + 3000, "helpful_vote": 3,
                       "rating": 4.0, "verified_purchase": False, "word_count": 4, "n_images": 0}


def test_null_text_word_count_is_zero(tmp_path, toy_gz):
    _, _, out = run(tmp_path, toy_gz, "--thin-every", "3")
    first = pq.read_table(out / "Toy_thin.parquet").to_pylist()[0]
    assert first["row_idx"] == NULL_TEXT_ROW and first["word_count"] == 0
    assert rp.ScanState("x").update({"timestamp": 1, "helpful_vote": 0, "text": None})


# 3. reservoir ---------------------------------------------------------------------------------------------------

def big_lines(n: int = 200) -> list[str]:
    return [json.dumps({"timestamp": MARCH_2019_MS + i, "helpful_vote": 0 if i % 2 else 2, "text": f"t{i}",
                        "parent_asin": f"P{i}", "asin": f"A{i}", "user_id": f"U{i}", "rating": 5.0})
            for i in range(n)]


def test_reservoir_cap_and_seed(tmp_path):
    src = write_gz(tmp_path / "Big.jsonl.gz", big_lines())

    def sample(seed: int, out: str):
        code, s, out_dir = run(tmp_path, src, "--keep-texts", "5", "--seed", str(seed), out=out)
        assert code == 0
        return s, pq.read_table(out_dir / "Toy_texts.parquet")

    s0, t0 = sample(0, "a")
    _, t0_again = sample(0, "b")
    _, t1 = sample(1, "c")

    assert s0["texts_seen"] == {"pos2": 100, "zero": 100}
    assert s0["texts_kept"] == {"pos2": 5, "zero": 5}
    strata = t0.column("stratum").to_pylist()
    assert strata.count("pos2") == 5 and strata.count("zero") == 5
    assert "user_id" not in t0.schema.names
    assert t0.schema.names == ["row_idx", "parent_asin", "asin", "timestamp_ms", "helpful_vote", "rating",
                               "verified_purchase", "word_count", "title", "text", "category", "stratum"]
    assert set(t0.column("category").to_pylist()) == {"Toy"}
    assert t0.to_pylist() == t0_again.to_pylist()
    assert sorted(t0.column("row_idx").to_pylist()) != sorted(t1.column("row_idx").to_pylist())


def test_one_vote_rows_not_kept(tmp_path, toy_gz):
    _, _, out = run(tmp_path, toy_gz, "--keep-texts", "100")
    votes = pq.read_table(out / "Toy_texts.parquet").column("helpful_vote").to_pylist()
    assert len(votes) == 30 and 1 not in votes


# 5. --max-rows ---------------------------------------------------------------------------------------------------

def test_max_rows_marks_incomplete(tmp_path, toy_gz):
    code, s, out = run(tmp_path, toy_gz, "--max-rows", "10")
    assert code == 0
    assert s["completed"] is False and s["error"] is None
    assert s["n_rows"] == 10
    assert (out / "Toy_thin.parquet").exists() and (out / "Toy_texts.parquet").exists()


# 6. gzip detected by magic bytes ----------------------------------------------------------------------------------

def test_plain_jsonl_and_magic_byte_detection(tmp_path, toy_gz):
    _, gz_summary, _ = run(tmp_path, toy_gz, out="gz")
    plain = write_plain(tmp_path / "Toy.jsonl", toy_lines())
    code, plain_summary, _ = run(tmp_path, plain, out="plain")
    disguised = write_gz(tmp_path / "Disguised.jsonl", toy_lines())  # gzip bytes, .jsonl name
    code2, disguised_summary, _ = run(tmp_path, disguised, out="disguised")
    assert code == code2 == 0
    for key in ("n_rows", "n_malformed", "helpful_vote_hist", "months", "ts_unit_counts", "texts_seen"):
        assert plain_summary[key] == gz_summary[key] == disguised_summary[key]


# 7. import hygiene -------------------------------------------------------------------------------------------------

def test_import_does_no_network_or_heavy_work():
    code = (
        "import socket, sys\n"
        "def _blocked(*a, **k): raise RuntimeError('network at import')\n"
        "socket.socket = _blocked; socket.create_connection = _blocked\n"
        "import ml.src.reviews_prepare\n"
        "heavy = [m for m in ('requests', 'pyarrow', 'pandas', 'orjson', 'tqdm') if m in sys.modules]\n"
        "assert not heavy, heavy\n"
    )
    env = {**os.environ, "PYTHONPATH": str(ROOT)}
    result = subprocess.run([sys.executable, "-c", code], cwd=ROOT, env=env, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


# 8. CLI, fallback and failure handling ------------------------------------------------------------------------------

def test_prepare_is_still_a_stub():
    with pytest.raises(NotImplementedError, match="TODO: Stage 4a"):
        rp.main(["prepare"])


def test_source_fallback_records_sources_tried(tmp_path, toy_gz, capsys):
    missing = tmp_path / "missing.jsonl.gz"
    args = rp.parse_args(["scan", "--category", "Toy", "--out", str(tmp_path / "out")])
    assert rp.scan(args, sources=[str(missing), str(toy_gz)]) == 0
    s = json.loads((tmp_path / "out" / "Toy_summary.json").read_text())
    assert s["completed"] is True and s["source"] == str(toy_gz)
    assert [t["source"] for t in s["sources_tried"]] == [str(missing), str(toy_gz)]
    assert s["sources_tried"][0]["error"].startswith("FileNotFoundError:")
    assert s["sources_tried"][1]["error"] is None
    assert f"WARNING: {missing} failed (FileNotFoundError" in capsys.readouterr().err


def test_fallback_note_when_next_source_is_hf(tmp_path, capsys, monkeypatch):
    def fail(src):
        raise ConnectionError("offline")

    monkeypatch.setattr(rp, "open_source", fail)
    args = rp.parse_args(["scan", "--category", "Toy", "--out", str(tmp_path / "out")])
    assert rp.scan(args) == 2  # every candidate fails; no network is touched
    err = capsys.readouterr().err
    assert "(uncompressed, ~3.5x larger download)" in err
    s = json.loads((tmp_path / "out" / "Toy_summary.json").read_text())
    assert [t["source"] for t in s["sources_tried"]] == rp.source_candidates(args)
    assert s["sources_tried"][-1]["source"].startswith(rp.HF_PREFIX)


def test_unreadable_input_exits_2_with_error(tmp_path):
    code, s, _ = run(tmp_path, tmp_path / "nope.jsonl.gz")
    assert code == 2
    assert s["completed"] is False and s["error"].startswith("FileNotFoundError:")


def test_source_candidates():
    args = rp.parse_args(["scan", "--category", "Office_Products"])
    ucsd = rp.source_candidates(args)
    assert len(ucsd) == 3 and ucsd[0].startswith("https://mcauleylab.ucsd.edu/") and ucsd[2].endswith(
        "/raw/review_categories/Office_Products.jsonl")
    args = rp.parse_args(["scan", "--category", "Office_Products", "--source", "hf"])
    assert rp.source_candidates(args) == [ucsd[2]]
    args = rp.parse_args(["scan", "--category", "X", "--input", "local.jsonl"])
    assert rp.source_candidates(args) == ["local.jsonl"]
