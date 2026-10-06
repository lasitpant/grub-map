import importlib
import json

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(tmp_path, monkeypatch):
    menus = {"aobaba": {"items": [{"id": "aobaba/pho", "price": 8.5, "lunch_deal": {}}]}}
    (tmp_path / "menus.json").write_text(json.dumps(menus))
    monkeypatch.setenv("MENUS_PATH", str(tmp_path / "menus.json"))
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "test.db"))
    monkeypatch.setenv("ADMIN_TOKEN", "secret")
    import grub_map_api.app as app_module
    importlib.reload(app_module)
    return TestClient(app_module.app), app_module


def test_vote_and_summary(client):
    c, _ = client
    assert c.post("/api/feedback", json={"item_id": "aobaba/pho", "kind": "still"}).status_code == 201
    assert c.post("/api/feedback", json={"item_id": "aobaba/pho", "kind": "changed", "price": 9.5}).status_code == 201
    s = c.get("/api/feedback").json()["aobaba/pho"]
    assert (s["still"], s["changed"]) == (1, 1)
    assert s["last_still"] and s["last_changed"]


def test_rejects_unknown_item_and_bad_price(client):
    c, _ = client
    assert c.post("/api/feedback", json={"item_id": "nope/x", "kind": "still"}).status_code == 404
    assert c.post("/api/feedback", json={"item_id": "aobaba/pho", "kind": "changed", "price": -1}).status_code == 422


def test_rate_limit(client):
    c, mod = client
    for _ in range(mod.RATE_LIMIT):
        assert c.post("/api/feedback", json={"item_id": "aobaba/pho", "kind": "still"}).status_code == 201
    assert c.post("/api/feedback", json={"item_id": "aobaba/pho", "kind": "still"}).status_code == 429


def test_admin_needs_token_and_stores_no_ip(client):
    c, mod = client
    c.post("/api/feedback", json={"item_id": "aobaba/pho", "kind": "changed", "price": 9.5})
    assert c.get("/api/admin/price-reports").status_code == 401
    r = c.get("/api/admin/price-reports", headers={"Authorization": "Bearer secret"})
    assert r.json()[0] | {"created_at": None} == {"item_id": "aobaba/pho", "reported_price": 9.5,
                                                  "created_at": None, "listed_price": 8.5}
    cols = [row[1] for row in mod.db().execute("PRAGMA table_info(votes)")]
    assert cols == ["id", "item_id", "kind", "reported_price", "created_at"]
