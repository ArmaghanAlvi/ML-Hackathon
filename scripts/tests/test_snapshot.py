"""Tests for scripts/snapshot.py. Fake secrets are assembled at runtime so this file itself stays clean."""
import subprocess
import zipfile

import pytest

from scripts import snapshot

FAKE_SERP = "SERPAPI" + "_KEY=" + "a1b2c3d4e5f6g7h8i9"
FAKE_HF = "hf" + "_" + "A" * 34
FAKE_PEM = "-----BEGIN " + "RSA PRIVATE KEY-----\nabc\n"


@pytest.mark.parametrize("path", [
    ".env", "backend/.env", ".env.local", "frontend/.env.production", "ml/data/catalog.parquet",
    "weights/head.pt", "x/emb.npy", "demo/backup_video.mp4", "labeling/queries/IMG_001.jpg",
    "frontend/node_modules/react/index.js", ".venv/bin/python", "frontend/dist/index.html",
    "backend/app/cache/abc.json", "snapshots/old.zip", "keys/server.pem", "gcp-credentials.json",
    ".git/config",
])
def test_denied(path):
    assert snapshot.is_denied(path)


@pytest.mark.parametrize("path", [
    ".env.example", "frontend/.env.example", "ml/data/.gitkeep", "labeling/queries/manifest.csv",
    "backend/app/main.py", "ml/artifacts/thresholds.json", "labeling/lens_cache/p01.json",
    "frontend/public/pwa-192x192.png", "shared/mocks/search_response.json",
    "docs/contracts.md", "docs/hackathon_roadmap.md", "docs/notes/stream-a.md", "CLAUDE.md",
])
def test_allowed(path):
    assert not snapshot.is_denied(path)


@pytest.mark.parametrize("content", [FAKE_SERP + "\n", "export " + FAKE_SERP + "\n", FAKE_PEM, "token = '" + FAKE_HF + "'\n"])
def test_secret_detected(tmp_path, content):
    f = tmp_path / "f.txt"
    f.write_text(content)
    assert snapshot.find_secret(f)


@pytest.mark.parametrize("content", [
    "SERPAPI_KEY=\n", "SERPAPI_KEY=your-key-here\n", "HF_MATCHER_REPO=team/matcher\n",
    'api_key = os.environ["SERPAPI_KEY"]\n', "password = getpass()\n",
])
def test_no_false_positive(tmp_path, content):
    f = tmp_path / "f.txt"
    f.write_text(content)
    assert snapshot.find_secret(f) is None


def test_repo_files_are_not_flagged():
    """The project's own tracked/untracked files must not trip the secret scan."""
    paths, _ = snapshot.candidate_files()
    flagged = [p for p in paths if (snapshot.REPO_ROOT / p).is_file() and snapshot.find_secret(snapshot.REPO_ROOT / p)]
    assert flagged == []


def _git(repo, *args):
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True)


def test_end_to_end_includes_uncommitted_and_excludes_unsafe(tmp_path, monkeypatch):
    repo = tmp_path / "proj"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.email", "t@example.com")
    _git(repo, "config", "user.name", "t")
    (repo / ".gitignore").write_text("ml/data/**\n!ml/data/.gitkeep\n")
    (repo / "committed.py").write_text("print('v1')\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "init")
    # working-tree changes after the commit
    (repo / "committed.py").write_text("print('v2 uncommitted')\n")
    (repo / "new_untracked.md").write_text("# new\n")
    (repo / ".env").write_text(FAKE_SERP + "\n")                      # not in .gitignore: denylist catches it
    (repo / "config.txt").write_text(FAKE_SERP + "\n")                # caught by the secret scan
    (repo / "ml" / "data").mkdir(parents=True)
    (repo / "ml" / "data" / ".gitkeep").write_text("")
    (repo / "ml" / "data" / "big.parquet").write_bytes(b"x" * 10)     # gitignored
    (repo / "model.pt").write_bytes(b"x" * 10)                        # denylisted weights

    monkeypatch.setattr(snapshot, "REPO_ROOT", repo)
    out = tmp_path / "out"
    assert snapshot.main(["--out", str(out), "--name", "test"]) == 0

    [zip_path] = list(out.glob("*.zip"))
    assert zip_path.name.endswith("-dirty-test.zip")
    with zipfile.ZipFile(zip_path) as zf:
        prefix = zip_path.stem + "/"
        names = {n.removeprefix(prefix) for n in zf.namelist()}
        assert {"committed.py", "new_untracked.md", ".gitignore", "ml/data/.gitkeep", "SNAPSHOT_INFO.txt"} <= names
        assert not names & {".env", "config.txt", "ml/data/big.parquet", "model.pt"}
        assert zf.read(prefix + "committed.py").decode() == "print('v2 uncommitted')\n"
        info = zf.read(prefix + "SNAPSHOT_INFO.txt").decode()
        assert "Uncommitted:     yes" in info and "Branch:          main" in info


def test_dry_run_writes_nothing(tmp_path, monkeypatch):
    out = tmp_path / "out"
    assert snapshot.main(["--dry-run", "--out", str(out)]) == 0
    assert not out.exists()
