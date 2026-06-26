from racedata import RaceRef, get_bronze_store
from racedata.local_store import LocalStore


def test_put_list_open_roundtrip(tmp_path):
    store = LocalStore(root=tmp_path)
    ref = RaceRef("cork", 2026, "full")
    assert not store.exists(ref)

    store.put(ref, b"%PDF-1.4 fake", source_url="https://example.com/results")

    assert store.exists(ref)
    assert [r.slug for r in store.list_races()] == ["cork_2026_full"]
    with store.open(ref) as fh:
        assert fh.read().startswith(b"%PDF")

    meta = (tmp_path / "cork" / "2026" / "meta.yaml").read_text()
    assert "sha256" in meta
    assert "source_url" in meta


def test_factory_default_is_local(monkeypatch, tmp_path):
    monkeypatch.delenv("BRONZE_BACKEND", raising=False)
    monkeypatch.setenv("BRONZE_ROOT", str(tmp_path))
    assert isinstance(get_bronze_store(), LocalStore)
