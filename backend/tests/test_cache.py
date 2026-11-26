from backend.app.services import cache


def test_key_is_deterministic_and_sensitive():
    k1 = cache.cache_key(b"img", "google_lens", None)
    assert k1 == cache.cache_key(b"img", "google_lens", "")
    assert len(k1) == 64
    assert k1 != cache.cache_key(b"img", "google_lens", "yellow")
    assert k1 != cache.cache_key(b"img", "google_shopping", None)
    assert k1 != cache.cache_key(b"img2", "google_lens", None)


def test_save_then_load_round_trips(tmp_path):
    key = cache.cache_key(b"abc", "google_lens", "red")
    data = {"visual_matches": [{"title": "x", "price": {"extracted_value": 9.99}}]}
    cache.save(key, data, cache_dir=tmp_path)
    assert cache.load(key, cache_dir=tmp_path) == data


def test_load_missing_returns_none(tmp_path):
    assert cache.load("0" * 64, cache_dir=tmp_path) is None


def test_uses_settings_cache_dir():
    key = cache.cache_key(b"settings", "google_lens", None)
    cache.save(key, {"ok": True})
    assert cache.load(key) == {"ok": True}
