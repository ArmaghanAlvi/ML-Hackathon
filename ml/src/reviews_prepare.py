"""reviews_prepare.py

Owner: Stream B · Roadmap: Stage 7a (team roadmap) · Stream B plan: `scan` = Stage 1a, `prepare` = Stage 4a
Purpose: profile the Amazon Reviews 2023 review files (`scan`), then sample and split the review-helpfulness
data (`prepare`).

scan (Stage 1a)
    Streams one category's raw review file (`{Category}.jsonl.gz`) in a single pass, without downloading it
    first, and writes three outputs to `--out` (default `ml/data/reviews/scan`, gitignored):

    * `{Category}_summary.json`: exact aggregates over every parsed row: row and malformed counts (plus the
      first 5 malformed lines, truncated to 200 chars, with the reason, in `malformed_examples`), timestamp
      range (with the detected unit per row), a helpful-vote histogram (0..49 and 50+), a rating histogram,
      the verified count, and per-month vote buckets (`n, v0, v1, v2, v3plus, v5plus, v10plus`).
    * `{Category}_thin.parquet`: every `--thin-every`-th parsed row, numeric columns only (no text).
    * `{Category}_texts.parquet`: a seeded reservoir sample (Algorithm R) of at most `--keep-texts` reviews per
      stratum: `pos2` (helpful_vote >= 2) and `zero` (helpful_vote == 0). Reviews with 1 vote aren't kept.
      NOTE: the reservoir is NOT at the natural class ratio (each stratum is capped separately). Stage 4a
      rebuilds the natural prevalence for validation and test using the `months` aggregates in the summary.

    Sources (`--input` overrides all of them): `--source ucsd` tries the primary UCSD host, then the second
    UCSD host, then the Hugging Face copy (uncompressed `.jsonl`, about 3.5x larger), moving on only if a
    source fails before any line is read. `--source hf` reads only the Hugging Face copy. Gzip is detected
    by its magic bytes, not by the file extension. Every attempt is recorded in `sources_tried`.

    Every `--checkpoint-every` parsed rows all outputs are rewritten atomically with `completed: false`, so a
    Colab disconnect leaves usable partial results (point `--out` at a mounted Drive folder). On EOF they are
    written with `completed: true`. On `--max-rows`: `completed: false`, `error: null`. On an error or Ctrl-C:
    `completed: false`, `error: "<type>: <message>"`, exit code 2.

    Standalone: this file runs on its own (e.g. copied into Colab). It needs only the stdlib plus `requests`
    (for URLs) and `pyarrow` (for the parquet outputs); `orjson` and `tqdm` are used if installed. All of
    them are imported lazily, so importing this module does no network or heavy work.

    Do NOT use `datasets.load_dataset` for this dataset: its HF repo relies on a loading script, which
    `datasets` 4.x no longer runs.

    Example:
        python ml/src/reviews_prepare.py scan --category Office_Products --max-rows 2000

prepare (Stage 4a)
    STUB: not implemented yet. Will sample ~50k reviews; helpful = >=3 votes, not helpful = 0 votes on
    old-enough reviews; split BY PRODUCT (`parent_asin`).
    Outputs: ml/data/reviews/{train,val,test}.parquet (text, label, parent_asin)
"""
from __future__ import annotations

import argparse
import array
import gzip
import io
import json
import os
import random
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

PRIMARY_URL = "https://mcauleylab.ucsd.edu/public_datasets/data/amazon_2023/raw/review_categories/{category}.jsonl.gz"
SECOND_URL = "https://datarepo.eng.ucsd.edu/mcauley_group/data/amazon_2023/raw/review_categories/{category}.jsonl.gz"
HF_URL = "https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023/resolve/main/raw/review_categories/{category}.jsonl"
HF_PREFIX = "https://huggingface.co/"

VOTE_BINS = 50                # histogram keys "0".."49", then "50+"
MS_THRESHOLD = 1e11           # timestamps above this are already milliseconds
DAY_MS = 86_400_000
GZIP_MAGIC = b"\x1f\x8b"
HTTP_TIMEOUT = (10, 120)      # (connect, read) seconds
READ_BUFFER = 1 << 20
MONTH_FIELDS = ("n", "v0", "v1", "v2", "v3plus", "v5plus", "v10plus")
STRATA = ("pos2", "zero")
INT16_MAX = 32767
INT32_MAX = 2**31 - 1
MALFORMED_EXAMPLES = 5        # malformed lines kept verbatim in the summary
MALFORMED_CHARS = 200         # ... each truncated to this many characters


# --------------------------------------------------------------------------- sources

def source_candidates(args: argparse.Namespace) -> list[str]:
    """Sources to try, in order. `--input` wins; otherwise depends on `--source`."""
    if args.input:
        return [args.input]
    fmt = {"category": args.category}
    if args.source == "hf":
        return [HF_URL.format(**fmt)]
    return [PRIMARY_URL.format(**fmt), SECOND_URL.format(**fmt), HF_URL.format(**fmt)]


def open_source(src: str):
    """Open `src` (http(s) URL or local path) as a raw binary stream. The only function that touches the network."""
    if src.startswith(("http://", "https://")):
        import requests  # lazy: only needed for URLs

        resp = requests.get(src, stream=True, timeout=HTTP_TIMEOUT)
        resp.raise_for_status()
        resp.raw.decode_content = False  # we detect and decompress gzip ourselves
        resp.raw.auto_close = False      # urllib3 otherwise marks the stream closed as soon as it hits EOF
        return _EOFSafeRaw(resp.raw)
    return open(src, "rb")


class _EOFSafeRaw(io.RawIOBase):
    """Wraps a network stream so that, once it has returned EOF, later reads return EOF again without touching it.

    Why: urllib3 (requests' `resp.raw`) closes itself when it reaches the end of the body. At the end of a gzip
    member, GzipFile reads once more to look for another member; BufferedReader then sees a closed raw stream and
    raises `ValueError: read of closed file`, which turned every complete scan into an error at EOF.
    Our own `closed` state only changes when `close()` is called.
    """

    def __init__(self, raw):
        self._raw = raw
        self._eof = False

    def readable(self) -> bool:
        return True

    def readinto(self, b) -> int:
        if self._eof:
            return 0
        n = self._raw.readinto(b)
        if not n:
            self._eof = True
            return 0
        return n

    def close(self) -> None:
        if not self.closed:
            try:
                self._raw.close()
            finally:
                super().close()


def _json_loads():
    try:
        import orjson  # lazy, optional (faster)

        return orjson.loads
    except ImportError:
        return json.loads


def iter_lines(stream, loads=None):
    """Yield `(line_no, raw_line, record, reason)` per non-blank line (line_no is 1-based, blank lines included).

    `record` is the parsed dict, or None with `reason` saying why the line isn't a JSON object.
    Gzip is detected by the first two bytes (1f 8b), not by the file name.
    """
    loads = loads or _json_loads()
    buf = stream if hasattr(stream, "peek") else io.BufferedReader(stream, READ_BUFFER)
    lines = gzip.GzipFile(fileobj=buf) if buf.peek(2)[:2] == GZIP_MAGIC else buf
    for line_no, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            obj = loads(line)
        except ValueError as exc:  # json/orjson JSONDecodeError and UnicodeDecodeError all subclass ValueError
            yield line_no, line, None, f"invalid JSON: {exc}"
            continue
        if isinstance(obj, dict):
            yield line_no, line, obj, None
        else:
            yield line_no, line, None, f"not a JSON object ({type(obj).__name__})"


def iter_records(stream, loads=None):
    """Yield one dict per non-blank line, or None for a line that isn't a JSON object."""
    for _, _, rec, _ in iter_lines(stream, loads):
        yield rec


# --------------------------------------------------------------------------- state

def _str_or_none(value):
    if value is None or isinstance(value, str):
        return value
    return str(value)


class ScanState:
    """Exact counters, the thin columnar sample and the per-stratum text reservoirs for one category."""

    def __init__(self, category: str, thin_every: int = 20, keep_texts: int = 100_000, seed: int = 0):
        self.category = category
        self.thin_every = max(1, int(thin_every))
        self.cap = max(0, int(keep_texts))
        self.rng = random.Random(seed)

        self.n_rows = 0                      # parsed rows; also the next row_idx
        self.n_malformed = 0
        self.malformed_examples: list[dict] = []  # first MALFORMED_EXAMPLES bad lines, for debugging
        self.ts_min_ms: int | None = None
        self.ts_max_ms: int | None = None
        self.ts_unit_counts = {"ms": 0, "s": 0}
        self.vote_hist = [0] * (VOTE_BINS + 1)
        self.rating_hist = [0] * 5
        self.n_verified = 0
        self.months: dict[str, list[int]] = {}   # "YYYY-MM" -> counts in MONTH_FIELDS order
        self._day_to_month: dict[int, str] = {}  # UTC day number -> "YYYY-MM" (avoids a datetime call per row)

        # Thin sample as typed columns (not per-row dicts), so ~3.4M rows stay small in memory.
        self.thin = {
            "row_idx": array.array("q"),
            "parent_asin": [],
            "timestamp_ms": array.array("q"),
            "helpful_vote": array.array("i"),
            "rating": array.array("f"),
            "verified_purchase": array.array("b"),
            "word_count": array.array("i"),
            "n_images": array.array("h"),
        }
        self.reservoir: dict[str, list[tuple]] = {s: [] for s in STRATA}
        self.texts_seen = {s: 0 for s in STRATA}

    def _month(self, ts_ms: int) -> str:
        day = ts_ms // DAY_MS
        key = self._day_to_month.get(day)
        if key is None:
            key = datetime.fromtimestamp(day * 86_400, tz=timezone.utc).strftime("%Y-%m")
            self._day_to_month[day] = key
        return key

    def _malformed(self, reason: str, raw=None, line_no: int | None = None) -> bool:
        self.n_malformed += 1
        if len(self.malformed_examples) < MALFORMED_EXAMPLES:
            if isinstance(raw, (bytes, bytearray)):
                raw = bytes(raw).decode("utf-8", errors="replace")
            self.malformed_examples.append({
                "line_no": line_no, "reason": reason,
                "line": None if raw is None else raw.rstrip("\r\n")[:MALFORMED_CHARS],
            })
        return False

    def update(self, rec: dict | None, raw=None, line_no: int | None = None, reason: str | None = None) -> bool:
        """Add one record. Returns True if it was parsed, False if counted as malformed.

        `raw`, `line_no` and `reason` (from `iter_lines`) are only used to describe malformed lines.
        """
        if rec is None:
            return self._malformed(reason or "not a JSON object", raw, line_no)
        for field in ("timestamp", "helpful_vote"):
            if field not in rec:
                return self._malformed(f"missing {field}", raw, line_no)
        try:
            ts = int(rec["timestamp"])
            votes = int(rec["helpful_vote"])
        except (TypeError, ValueError) as exc:
            return self._malformed(f"bad timestamp/helpful_vote: {type(exc).__name__}: {exc}", raw, line_no)
        if votes < 0:
            return self._malformed(f"negative helpful_vote ({votes})", raw, line_no)

        row_idx = self.n_rows

        if ts > MS_THRESHOLD:
            ts_ms = ts
            self.ts_unit_counts["ms"] += 1
        else:
            ts_ms = ts * 1000
            self.ts_unit_counts["s"] += 1
        if self.ts_min_ms is None or ts_ms < self.ts_min_ms:
            self.ts_min_ms = ts_ms
        if self.ts_max_ms is None or ts_ms > self.ts_max_ms:
            self.ts_max_ms = ts_ms

        text = rec.get("text")
        text = text if isinstance(text, str) else None
        # Must match the length heuristic in ml/inference/reviews.py
        # (score_reviews today; it moves to length_score in Breakdown 1 Step 6).
        word_count = len((text or "").split())
        images = rec.get("images")
        n_images = len(images) if isinstance(images, list) else 0

        try:
            rating = float(rec.get("rating"))
        except (TypeError, ValueError):
            rating = float("nan")
        if rating == rating:  # not NaN
            star = int(round(rating))
            if 1 <= star <= 5:
                self.rating_hist[star - 1] += 1
        verified = bool(rec.get("verified_purchase"))
        if verified:
            self.n_verified += 1

        self.vote_hist[min(votes, VOTE_BINS)] += 1

        bucket = self.months.get(key := self._month(ts_ms))
        if bucket is None:
            bucket = self.months[key] = [0] * len(MONTH_FIELDS)
        bucket[0] += 1
        if votes <= 2:
            bucket[1 + votes] += 1          # v0 / v1 / v2 are exact
        else:
            bucket[4] += 1                  # v3plus, v5plus, v10plus are cumulative
            if votes >= 5:
                bucket[5] += 1
            if votes >= 10:
                bucket[6] += 1

        parent_asin = _str_or_none(rec.get("parent_asin"))

        if row_idx % self.thin_every == 0:
            t = self.thin
            t["row_idx"].append(row_idx)
            t["parent_asin"].append(parent_asin)
            t["timestamp_ms"].append(ts_ms)
            t["helpful_vote"].append(min(votes, INT32_MAX))
            t["rating"].append(rating)
            t["verified_purchase"].append(1 if verified else 0)
            t["word_count"].append(min(word_count, INT32_MAX))
            t["n_images"].append(min(n_images, INT16_MAX))

        if self.cap:
            stratum = "pos2" if votes >= 2 else "zero" if votes == 0 else None
            if stratum is not None:
                # Algorithm R: the i-th item (0-based) replaces a random slot with probability cap / (i + 1),
                # so after any number of items every item seen so far is in the sample with equal probability.
                i = self.texts_seen[stratum]
                self.texts_seen[stratum] = i + 1
                item = (row_idx, parent_asin, _str_or_none(rec.get("asin")), ts_ms, votes, rating, verified,
                        word_count, _str_or_none(rec.get("title")), text, self.category, stratum)
                slots = self.reservoir[stratum]
                if i < self.cap:
                    slots.append(item)
                else:
                    j = self.rng.randint(0, i)
                    if j < self.cap:
                        slots[j] = item

        self.n_rows = row_idx + 1
        return True

    # ----------------------------------------------------------------------- outputs

    def summary(self, completed: bool, error: str | None, meta: dict | None = None) -> dict:
        meta = meta or {}
        seconds = float(meta.get("seconds", 0.0))
        hist = {str(k): self.vote_hist[k] for k in range(VOTE_BINS)}
        hist[f"{VOTE_BINS}+"] = self.vote_hist[VOTE_BINS]
        return {
            "category": self.category,
            "source": meta.get("source"),
            "sources_tried": meta.get("sources_tried", []),
            "completed": completed,
            "error": error,
            "args": meta.get("args", {}),
            "started_at": meta.get("started_at"),
            "finished_at": meta.get("finished_at"),
            "seconds": round(seconds, 3),
            "rows_per_sec": round(self.n_rows / seconds, 1) if seconds > 0 else 0.0,
            "n_rows": self.n_rows,
            "n_malformed": self.n_malformed,
            "malformed_examples": list(self.malformed_examples),
            "ts_min_ms": self.ts_min_ms,
            "ts_max_ms": self.ts_max_ms,
            "ts_unit_counts": dict(self.ts_unit_counts),
            "helpful_vote_hist": hist,
            "rating_hist": {str(i + 1): n for i, n in enumerate(self.rating_hist)},
            "n_verified": self.n_verified,
            "months": {k: dict(zip(MONTH_FIELDS, v)) for k, v in sorted(self.months.items())},
            "thin_every": self.thin_every,
            "n_thin": len(self.thin["row_idx"]),
            "texts_cap": self.cap,
            "texts_seen": dict(self.texts_seen),
            "texts_kept": {s: len(self.reservoir[s]) for s in STRATA},
        }

    def _thin_table(self):
        import pyarrow as pa

        t, n = self.thin, len(self.thin["row_idx"])

        def col(name, typ):  # copy the typed array's bytes straight into an Arrow array
            return pa.Array.from_buffers(typ, n, [None, pa.py_buffer(t[name].tobytes())])

        return pa.table({
            "row_idx": col("row_idx", pa.int64()),
            "parent_asin": pa.array(t["parent_asin"], type=pa.string()),
            "timestamp_ms": col("timestamp_ms", pa.int64()),
            "helpful_vote": col("helpful_vote", pa.int32()),
            "rating": col("rating", pa.float32()),
            "verified_purchase": col("verified_purchase", pa.int8()).cast(pa.bool_()),
            "word_count": col("word_count", pa.int32()),
            "n_images": col("n_images", pa.int16()),
        })

    def _texts_table(self):
        import pyarrow as pa

        schema = pa.schema([
            ("row_idx", pa.int64()), ("parent_asin", pa.string()), ("asin", pa.string()),
            ("timestamp_ms", pa.int64()), ("helpful_vote", pa.int32()), ("rating", pa.float32()),
            ("verified_purchase", pa.bool_()), ("word_count", pa.int32()), ("title", pa.string()),
            ("text", pa.string()), ("category", pa.string()), ("stratum", pa.string()),
        ])
        rows = [item for s in STRATA for item in self.reservoir[s]]
        columns = list(zip(*rows)) if rows else [()] * len(schema)
        return pa.table([pa.array(list(c), type=f.type) for c, f in zip(columns, schema)], schema=schema)

    def write(self, out, completed: bool, error: str | None = None, meta: dict | None = None) -> dict:
        """Write all outputs atomically (temp file + os.replace). The summary is written last."""
        import pyarrow.parquet as pq

        out = Path(out)
        out.mkdir(parents=True, exist_ok=True)
        stem = out / self.category
        _atomic(Path(f"{stem}_thin.parquet"), lambda p: pq.write_table(self._thin_table(), p))
        if self.cap:
            _atomic(Path(f"{stem}_texts.parquet"), lambda p: pq.write_table(self._texts_table(), p))
        summary = self.summary(completed, error, meta)
        _atomic(Path(f"{stem}_summary.json"),
                lambda p: p.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"))
        return summary


def _atomic(path: Path, writer) -> None:
    tmp = path.with_name(path.name + ".tmp")
    writer(tmp)
    os.replace(tmp, path)


# --------------------------------------------------------------------------- progress + scan

class _Progress:
    """tqdm bar if available, else a print every 1M rows."""

    def __init__(self, desc: str):
        self.shown = 0
        try:
            from tqdm import tqdm  # lazy, optional

            self.bar = tqdm(desc=desc, unit=" rows", unit_scale=True, mininterval=2.0)
        except ImportError:
            self.bar = None
            self.t0 = time.monotonic()

    def update(self, n_rows: int) -> None:
        if self.bar is not None:
            self.bar.update(n_rows - self.shown)
            self.shown = n_rows
        elif n_rows - self.shown >= 1_000_000:
            rate = n_rows / max(time.monotonic() - self.t0, 1e-9)
            print(f"  {n_rows:,} rows ({rate:,.0f} rows/s)", flush=True)
            self.shown = n_rows

    def close(self, n_rows: int) -> None:
        if self.bar is not None:
            self.bar.update(n_rows - self.shown)
            self.bar.close()


def _err(exc: BaseException) -> str:
    return f"{type(exc).__name__}: {exc}"


def _day(ms: int | None) -> str:
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime("%Y-%m-%d") if ms is not None else "n/a"


def final_line(summary: dict) -> str:
    n = summary["n_rows"]
    zero = 100.0 * summary["helpful_vote_hist"]["0"] / n if n else 0.0
    return (f"{summary['category']}: rows={n:,}, completed={summary['completed']}, "
            f"ts={_day(summary['ts_min_ms'])}→{_day(summary['ts_max_ms'])}, "
            f"zero_votes={zero:.1f}%, rows/s={summary['rows_per_sec']:,.0f}")


def scan(args: argparse.Namespace, sources: list[str] | None = None) -> int:
    """Run the scan. `sources` overrides the candidate list (used by tests). Returns the exit code."""
    sources = list(sources) if sources is not None else source_candidates(args)
    loads = _json_loads()
    state = ScanState(args.category, args.thin_every, args.keep_texts, args.seed)
    run_args = {k: v for k, v in vars(args).items() if k != "func"}
    started_at = datetime.now(timezone.utc)
    t0 = time.monotonic()
    tried: list[dict] = []
    used: str | None = None

    def meta() -> dict:
        return {
            "source": used, "sources_tried": list(tried), "args": run_args,
            "started_at": started_at.isoformat(timespec="seconds"),
            "finished_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "seconds": time.monotonic() - t0,
        }

    progress = _Progress(args.category)
    checkpoint_every = args.checkpoint_every or 0
    max_rows = args.max_rows
    hit_max = False
    try:
        for k, src in enumerate(sources):
            consumed = 0
            try:
                stream = open_source(src)
                used = src
                try:
                    for line_no, raw, rec, reason in iter_lines(stream, loads):
                        consumed += 1
                        if not state.update(rec, raw, line_no, reason):
                            continue
                        n = state.n_rows
                        if n % 10_000 == 0:
                            progress.update(n)
                        if checkpoint_every and n % checkpoint_every == 0:
                            state.write(args.out, False, None, meta())
                        if max_rows and n >= max_rows:
                            hit_max = True
                            break
                finally:
                    stream.close()
            except Exception as exc:
                tried.append({"source": src, "error": _err(exc)})
                if consumed == 0 and k + 1 < len(sources):
                    used = None
                    nxt = sources[k + 1]
                    note = " (uncompressed, ~3.5x larger download)" if nxt.startswith(HF_PREFIX) else ""
                    print(f"WARNING: {src} failed ({_err(exc)}); trying {nxt}{note}", file=sys.stderr, flush=True)
                    continue
                raise
            tried.append({"source": src, "error": None})
            break
    except (Exception, KeyboardInterrupt) as exc:
        progress.close(state.n_rows)
        summary = state.write(args.out, False, _err(exc), meta())
        print(final_line(summary))
        print(f"ERROR: {summary['error']}", file=sys.stderr)
        return 2

    progress.close(state.n_rows)
    summary = state.write(args.out, not hit_max, None, meta())
    print(final_line(summary))
    return 0


# --------------------------------------------------------------------------- prepare (stub) + CLI

def prepare(args: argparse.Namespace) -> int:
    raise NotImplementedError("TODO: Stage 4a")


def _positive(value: str) -> int:
    n = int(value)
    if n < 1:
        raise argparse.ArgumentTypeError("must be >= 1")
    return n


def _non_negative(value: str) -> int:
    n = int(value)
    if n < 0:
        raise argparse.ArgumentTypeError("must be >= 0")
    return n


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="reviews_prepare.py", description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)

    s = sub.add_parser("scan", help="Stream one category's raw review file and profile it (Stage 1a).",
                       description="Stream one Amazon Reviews 2023 category file in a single pass and write "
                                   "{Category}_summary.json, {Category}_thin.parquet and {Category}_texts.parquet.")
    s.add_argument("--category", required=True, help="Category file name without extension, e.g. Office_Products")
    s.add_argument("--input", help="http(s) URL or local path; overrides --source")
    s.add_argument("--source", choices=["ucsd", "hf"], default="ucsd",
                   help="ucsd: primary host, then second host, then HF (default). hf: Hugging Face copy only.")
    s.add_argument("--out", default="ml/data/reviews/scan", help="Output folder (default: %(default)s)")
    s.add_argument("--max-rows", type=_positive, default=None, help="Stop after N parsed rows (completed=false)")
    s.add_argument("--thin-every", type=_positive, default=20, help="Keep every k-th parsed row (default: %(default)s)")
    s.add_argument("--keep-texts", type=_non_negative, default=100_000,
                   help="Reservoir cap per stratum; 0 = no texts file (default: %(default)s)")
    s.add_argument("--checkpoint-every", type=_non_negative, default=2_000_000,
                   help="Rewrite outputs every N parsed rows; 0 = only at the end (default: %(default)s)")
    s.add_argument("--seed", type=int, default=0, help="Reservoir sampling seed (default: %(default)s)")
    s.set_defaults(func=scan)

    p = sub.add_parser("prepare", help="STUB: sample and split review-helpfulness data (Stage 4a).")
    p.add_argument("--n", type=int, default=50000, help="Number of reviews")
    p.add_argument("--out-dir", default="ml/data/reviews", help="Output dir")
    p.set_defaults(func=prepare)
    return parser


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    return build_parser().parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
