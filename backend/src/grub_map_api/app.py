"""Grub Map API: anonymous "still this price?" votes on lunch deals.

Privacy: no accounts, no cookies, and no IP addresses or user agents are stored.
Rate limiting uses a salted hash of the IP that lives only in memory and the salt rotates daily,
so it can't be linked back to a person or across days.
"""
import hashlib
import json
import os
import secrets
import sqlite3
import time
from collections import defaultdict, deque
from contextlib import closing
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Literal

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[3]
DB_PATH = Path(os.environ.get("DATABASE_PATH", ROOT / "backend" / "grubmap.db"))
MENUS_PATH = Path(os.environ.get("MENUS_PATH", ROOT / "web" / "public" / "data" / "menus.json"))
ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "")
WINDOW_DAYS = 60       # votes older than this don't count toward the summary
RATE_LIMIT = 30        # votes per client per hour

app = FastAPI(title="Grub Map API", docs_url="/api/docs", openapi_url="/api/openapi.json")
app.add_middleware(CORSMiddleware, allow_origins=ALLOWED_ORIGINS, allow_methods=["GET", "POST"],
                   allow_headers=["Content-Type", "Authorization"])


# --- storage ---------------------------------------------------------------

def db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with closing(db()) as conn, conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS votes (
                id INTEGER PRIMARY KEY,
                item_id TEXT NOT NULL,
                kind TEXT NOT NULL CHECK (kind IN ('still', 'changed')),
                reported_price REAL,
                created_at TEXT NOT NULL
            )""")
        conn.execute("CREATE INDEX IF NOT EXISTS votes_item ON votes (item_id, created_at)")


def known_items() -> dict[str, float]:
    """Deal ids and prices from the exported menus, so votes can't target made-up items."""
    menus = json.loads(MENUS_PATH.read_text())
    return {i["id"]: i["price"] for m in menus.values() for i in m["items"] if i.get("lunch_deal") is not None}


init_db()
ITEMS = known_items()


# --- rate limiting (memory only) -------------------------------------------

_salt = {"day": None, "value": b""}
_hits: dict[str, deque] = defaultdict(deque)


def client_key(request: Request) -> str:
    today = date.today()
    if _salt["day"] != today:  # new salt each day; yesterday's keys become meaningless
        _salt.update(day=today, value=secrets.token_bytes(16))
        _hits.clear()
    ip = request.headers.get("cf-connecting-ip") or (request.client.host if request.client else "")
    return hashlib.sha256(_salt["value"] + ip.encode()).hexdigest()[:16]


def rate_limit(request: Request) -> None:
    hits, now = _hits[client_key(request)], time.monotonic()
    while hits and now - hits[0] > 3600:
        hits.popleft()
    if len(hits) >= RATE_LIMIT:
        raise HTTPException(429, "Too many votes from this connection. Try again in an hour.")
    hits.append(now)


# --- API -------------------------------------------------------------------

class Vote(BaseModel):
    item_id: str = Field(max_length=200)
    kind: Literal["still", "changed"]
    price: float | None = Field(default=None, gt=0, le=100, description="New price, when kind is 'changed'")


@app.get("/api/health")
def health():
    return {"ok": True, "items": len(ITEMS)}


@app.get("/api/feedback")
def feedback_summary():
    """Per deal: recent 'still this price' and 'price changed' counts, and when each last happened."""
    since = (datetime.now(timezone.utc) - timedelta(days=WINDOW_DAYS)).isoformat()
    with closing(db()) as conn:
        rows = conn.execute("""
            SELECT item_id, kind, COUNT(*) AS n, MAX(created_at) AS last
            FROM votes WHERE created_at >= ? GROUP BY item_id, kind""", (since,)).fetchall()
    out: dict[str, dict] = {}
    for r in rows:
        s = out.setdefault(r["item_id"], {"still": 0, "changed": 0, "last_still": None, "last_changed": None})
        s[r["kind"]] = r["n"]
        s[f"last_{r['kind']}"] = r["last"]
    return out


@app.post("/api/feedback", status_code=201, dependencies=[Depends(rate_limit)])
def add_feedback(vote: Vote):
    if vote.item_id not in ITEMS:
        raise HTTPException(404, "Unknown deal.")
    price = vote.price if vote.kind == "changed" else None
    with closing(db()) as conn, conn:
        conn.execute("INSERT INTO votes (item_id, kind, reported_price, created_at) VALUES (?, ?, ?, ?)",
                     (vote.item_id, vote.kind, price, datetime.now(timezone.utc).isoformat()))
    return {"ok": True}


def require_admin(authorization: str = Header(default="")) -> None:
    if not ADMIN_TOKEN or not secrets.compare_digest(authorization, f"Bearer {ADMIN_TOKEN}"):
        raise HTTPException(401, "Admin token required.")


@app.get("/api/admin/price-reports", dependencies=[Depends(require_admin)])
def price_reports(days: int = 30):
    """'Price changed' reports for review, newest first, with the price we currently show."""
    since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    with closing(db()) as conn:
        rows = conn.execute("""
            SELECT item_id, reported_price, created_at FROM votes
            WHERE kind = 'changed' AND created_at >= ? ORDER BY created_at DESC""", (since,)).fetchall()
    return [{**dict(r), "listed_price": ITEMS.get(r["item_id"])} for r in rows]
