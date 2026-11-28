"""snapshot.py: make a safe zip snapshot of the project as it is on disk right now.

Owner: Shared tooling · Not part of the ML/backend/frontend contracts.

The snapshot captures your *working tree*, not the remote: committed files, uncommitted edits
and new (untracked) files are all included, whether or not your branch is caught up with GitHub.
Nothing is fetched or pushed; the script never touches the network or changes git state.

What makes it "safe":
  1. File selection follows .gitignore (via `git ls-files --cached --others --exclude-standard`),
     so .venv/, node_modules/, frontend/dist/, ml/data/, caches and weights are left out.
  2. A hard denylist runs on top of that, in case .gitignore is wrong or missing: secrets (.env,
     keys, credentials), datasets, weights, media, real photos in labeling/queries/, build output.
  3. Text files are scanned for filled-in secrets (e.g. `SERPAPI_KEY=abc...`, private key blocks);
     any hit is skipped and reported.
  4. Files larger than --max-mb (default 25) are skipped and reported.

File names say which branch the snapshot is of and number snapshots per branch:
    <project>_<branch>_snapshot-<NNN>_<YYYY-MM-DD>_<HHMM>[_uncommitted][_<label>].zip
    e.g. ML-Hackathon_stream-b-eval_snapshot-003_2026-11-26_1432_uncommitted.zip
- <branch> is the current branch with "/" turned into "-" (detached HEAD -> detached-<sha>).
- <NNN> is one more than the highest number already in the output folder for that branch, so
  numbers count up per branch and are never reused, even if you delete an older zip.
- The time is your local time; "_uncommitted" means the working tree had changes not yet committed.

Every zip contains SNAPSHOT_INFO.txt: snapshot number, branch, commit, upstream ahead/behind (from
the last fetch), uncommitted changes, and the full list of included and skipped files.

Usage (from the repo root, plain Python 3.11+, no venv needed):
    python scripts/snapshot.py                 # -> snapshots/<project>_<branch>_snapshot-<NNN>_....zip
    python scripts/snapshot.py --dry-run       # list what would be included/skipped, write nothing
    python scripts/snapshot.py --out ~/Desktop --name before-merge
"""
from __future__ import annotations

import argparse
import fnmatch
import os
import re
import subprocess
import sys
import zipfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = "snapshots"
DEFAULT_MAX_MB = 25.0

# Paths (repo-relative, forward slashes) that are never included, whatever .gitignore says.
DENY_GLOBS = [
    # secrets
    ".env", "*/.env", ".env.*", "*/.env.*", "*.pem", "*.key", "*.p12", "*.pfx",
    "id_rsa*", "*/id_rsa*", "*credentials*.json", "*secret*.json", "*service-account*.json",
    ".netrc", ".npmrc", ".pypirc", ".claude/settings.local.json",
    # environments, dependencies, build output, caches
    ".git/*", ".venv/*", "venv/*", "*/node_modules/*", "node_modules/*", "frontend/dist/*",
    "frontend/dev-dist/*", "*__pycache__/*", "*.pyc", ".pytest_cache/*", "*/.ipynb_checkpoints/*",
    # data, weights, media, real photos, API caches, previous snapshots
    "ml/data/*", "backend/app/cache/*.json", "labeling/queries/*", "snapshots/*",
    "*.pt", "*.pth", "*.safetensors", "*.ckpt", "*.bin", "*.npy", "*.npz", "*.onnx", "*.parquet",
    "*.h5", "*.pkl", "*.mp4", "*.mov", "*.zip", "*.tar", "*.tar.gz", "*.tgz", "*.7z",
]
# Explicit exceptions to DENY_GLOBS (templates and placeholders that are meant to be shared).
ALLOW_GLOBS = ["*.env.example", ".env.example", "*/.gitkeep", ".gitkeep", "labeling/queries/manifest.csv"]

# Env-style assignment of a secret-named key (KEY=value or KEY: value, value 8+ token-like chars,
# then end of line / whitespace / comment). Upper-case keys only, so ordinary code doesn't match.
SECRET_ASSIGNMENT = re.compile(
    r"^[ \t]*(?:export[ \t]+)?"
    r"(?P<key>[A-Z0-9_]*(?:API_KEY|_TOKEN|SECRET|PASSWORD|PRIVATE_KEY)[A-Z0-9_]*)"
    r"[ \t]*[=:][ \t]*['\"]?(?P<value>[A-Za-z0-9_\-./+=]{8,})['\"]?[ \t]*(?:#.*)?$",
    re.M,
)
PLACEHOLDER = re.compile(r"^(?:your|change|replace|example|placeholder|dummy|fake|test|xxx|tbd|none|null)", re.I)
SECRET_PATTERNS = [
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"\bhf_[A-Za-z0-9]{30,}\b"),            # Hugging Face token
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b"),      # GitHub token
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),            # OpenAI/Anthropic-style key
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),                 # AWS access key id
]
SCAN_MAX_BYTES = 2_000_000  # only scan text files up to this size (bigger ones are skipped anyway)


@dataclass
class Selection:
    included: list[str] = field(default_factory=list)
    skipped: list[tuple[str, str]] = field(default_factory=list)  # (path, reason)


def _git(*args: str) -> str | None:
    try:
        out = subprocess.run(["git", *args], cwd=REPO_ROOT, capture_output=True, text=True, check=True)
    except (OSError, subprocess.CalledProcessError):
        return None
    return out.stdout.rstrip("\n")  # keep leading spaces: they matter in `git status --porcelain`


def _matches(path: str, globs: list[str]) -> bool:
    name = path.rsplit("/", 1)[-1]
    return any(fnmatch.fnmatchcase(path, g) or fnmatch.fnmatchcase(name, g) for g in globs)


def is_denied(path: str) -> bool:
    return _matches(path, DENY_GLOBS) and not _matches(path, ALLOW_GLOBS)


def find_secret(path: Path) -> str | None:
    """Return a short description of the first secret-looking content in `path`, or None."""
    try:
        if path.stat().st_size > SCAN_MAX_BYTES:
            return None
        data = path.read_bytes()
    except OSError:
        return None
    if b"\0" in data[:8192]:  # binary file
        return None
    text = data.decode("utf-8", errors="ignore")
    for m in SECRET_ASSIGNMENT.finditer(text):
        if not PLACEHOLDER.match(m.group("value")):
            line = text.count("\n", 0, m.start()) + 1
            return f"{m.group('key')} has a value on line {line}"
    for pat in SECRET_PATTERNS:
        m = pat.search(text)
        if m:
            line = text.count("\n", 0, m.start()) + 1
            return f"looks like a secret on line {line}"
    return None


def candidate_files() -> tuple[list[str], bool]:
    """Repo-relative paths to consider, and whether git was used to pick them."""
    out = _git("ls-files", "--cached", "--others", "--exclude-standard", "-z")
    if out is not None:
        return sorted({p for p in out.split("\0") if p}), True
    # No git (or not a repo): walk the tree; the denylist does all the filtering.
    paths = []
    for dirpath, dirnames, filenames in os.walk(REPO_ROOT):
        rel_dir = Path(dirpath).relative_to(REPO_ROOT).as_posix()
        join = (lambda n: n) if rel_dir == "." else (lambda n: f"{rel_dir}/{n}")
        dirnames[:] = [d for d in dirnames if not is_denied(join(d) + "/x")]
        paths.extend(join(f) for f in filenames)
    return sorted(paths), False


def select_files(paths: list[str], max_mb: float) -> Selection:
    sel = Selection()
    max_bytes = int(max_mb * 1024 * 1024)
    for rel in paths:
        p = REPO_ROOT / rel
        if p.is_symlink():
            sel.skipped.append((rel, "symlink"))
            continue
        if not p.is_file():
            continue  # tracked but deleted in the working tree: the snapshot reflects disk
        if is_denied(rel):
            sel.skipped.append((rel, "denylist (secret/data/weights/build output)"))
            continue
        size = p.stat().st_size
        if size > max_bytes:
            sel.skipped.append((rel, f"larger than {max_mb:g} MB ({size / 1024 / 1024:.1f} MB)"))
            continue
        secret = find_secret(p)
        if secret:
            sel.skipped.append((rel, secret))
            continue
        sel.included.append(rel)
    return sel


def git_summary() -> dict[str, str]:
    info = {"branch": "n/a", "commit": "n/a", "short": "nogit", "upstream": "none",
            "ahead_behind": "n/a", "dirty": "unknown", "status": ""}
    commit = _git("rev-parse", "HEAD")
    if commit is None:
        return info
    info["commit"] = commit
    info["short"] = commit[:7]
    info["branch"] = _git("rev-parse", "--abbrev-ref", "HEAD") or "n/a"
    upstream = _git("rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}")
    if upstream:
        info["upstream"] = upstream
        counts = _git("rev-list", "--left-right", "--count", "HEAD...@{u}")
        if counts:
            ahead, behind = counts.split()
            info["ahead_behind"] = f"{ahead} ahead, {behind} behind (as of your last `git fetch`)"
    status = _git("status", "--porcelain") or ""
    info["status"] = status
    info["dirty"] = "yes" if status else "no"
    return info


def _slug(text: str) -> str:
    """File-name-safe version of `text` (anything outside [A-Za-z0-9._-] becomes '-')."""
    return re.sub(r"[^A-Za-z0-9._-]+", "-", text).strip("-") or "unnamed"


def branch_label(git: dict[str, str]) -> str:
    """Branch part of the file name: stream/b-eval -> stream-b-eval."""
    if git["branch"] == "n/a":
        return "no-git"
    if git["branch"] == "HEAD":  # detached HEAD
        return f"detached-{git['short']}"
    return _slug(git["branch"])


def next_number(out_dir: Path, project: str, branch: str) -> int:
    """One more than the highest snapshot number already in `out_dir` for this project + branch."""
    pattern = re.compile(rf"^{re.escape(project)}_{re.escape(branch)}_snapshot-(\d+)(?:_|\.zip$)")
    numbers = [int(m.group(1)) for p in out_dir.glob("*.zip") if (m := pattern.match(p.name))]
    return max(numbers, default=0) + 1


def snapshot_stem(project: str, branch: str, number: int, when: datetime, dirty: bool, label: str | None) -> str:
    parts = [project, branch, f"snapshot-{number:03d}", when.strftime("%Y-%m-%d_%H%M")]
    if dirty:
        parts.append("uncommitted")
    if label:
        parts.append(_slug(label))
    return "_".join(parts)


def build_info(git: dict[str, str], sel: Selection, created: datetime, number: int) -> str:
    lines = [
        "Project snapshot",
        "================",
        f"Snapshot:        #{number} for branch {git['branch']}",
        f"Created (local): {created.astimezone().isoformat(timespec='seconds')}",
        f"Created (UTC):   {created.isoformat(timespec='seconds')}",
        f"Branch:          {git['branch']}",
        f"Commit (HEAD):   {git['commit']}",
        f"Upstream:        {git['upstream']}",
        f"Ahead/behind:    {git['ahead_behind']}",
        f"Uncommitted:     {git['dirty']}",
        "",
        "This zip holds the working tree as it was on disk (including uncommitted and untracked",
        "files), filtered by .gitignore, a safety denylist and a secret scan. It is not a git clone.",
        "",
        "git status --porcelain at snapshot time:",
        *(f"  {line}" for line in (git["status"].splitlines() or ["(clean)"])),
        "",
        f"Included files ({len(sel.included)}):",
        *(f"  {p}" for p in sel.included),
        "",
        f"Skipped files ({len(sel.skipped)}):",
        *(f"  {p}  [{why}]" for p, why in sel.skipped),
        "",
    ]
    return "\n".join(lines)


def write_zip(dest: Path, prefix: str, sel: Selection, info: str) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(".zip.part")
    with zipfile.ZipFile(tmp, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        zf.writestr(f"{prefix}/SNAPSHOT_INFO.txt", info)
        for rel in sel.included:
            zf.write(REPO_ROOT / rel, f"{prefix}/{rel}")
    tmp.replace(dest)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Make a safe zip snapshot of the working tree.")
    parser.add_argument("--out", default=DEFAULT_OUT, help=f"Output folder (default: {DEFAULT_OUT}/, gitignored)")
    parser.add_argument("--name", help="Optional label added to the file name, e.g. before-merge")
    parser.add_argument("--max-mb", type=float, default=DEFAULT_MAX_MB, help="Skip files larger than this")
    parser.add_argument("--dry-run", action="store_true", help="Only list what would be included/skipped")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    paths, used_git = candidate_files()
    if not used_git:
        print("warning: git not available; selecting files by denylist only", file=sys.stderr)
    sel = select_files(paths, args.max_mb)
    git = git_summary()
    created = datetime.now(timezone.utc)

    out_dir = Path(args.out).expanduser()
    if not out_dir.is_absolute():
        out_dir = REPO_ROOT / out_dir
    project = _slug(REPO_ROOT.name)
    branch = branch_label(git)
    number = next_number(out_dir, project, branch)
    stem = snapshot_stem(project, branch, number, created.astimezone(), git["dirty"] == "yes", args.name)
    dest = out_dir / f"{stem}.zip"

    for p, why in sel.skipped:
        print(f"skip  {p}  [{why}]")
    if args.dry_run:
        for p in sel.included:
            print(f"keep  {p}")
        print(f"\n{len(sel.included)} files would be included, {len(sel.skipped)} skipped (dry run, nothing written)")
        print(f"Would write: {dest.name}")
        return 0

    write_zip(dest, stem, sel, build_info(git, sel, created, number))
    size_mb = dest.stat().st_size / 1024 / 1024
    print(f"\nWrote {dest} ({size_mb:.2f} MB): {len(sel.included)} files included, {len(sel.skipped)} skipped.")
    print(f"Snapshot #{number} of branch {git['branch']} @ {git['short']}, uncommitted changes: {git['dirty']}, "
          f"upstream: {git['ahead_behind']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
