"""Merge curated deals (data/deals.csv) with OSM venues and export JSON for the Vue app.

Output (web/public/data/):
  venues.json   – one row per physical location (chains get one row per branch)
  menus.json    – menus keyed by brand; items flagged with `lunch_deal` when they are a lunch offer
  basemap.geojson
These files mirror the shape a future API would return, so the frontend only swaps its fetch URLs.
"""
import csv, json, re, shutil
from datetime import date
from pathlib import Path

HERE = Path(__file__).parent
DATA = HERE / "data"
OUT = HERE.parent / "web" / "public" / "data"

def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")

def dedupe(hits, metres=60):
    """OSM often maps a branch twice (a node and a building way); keep one per ~60 m."""
    kept = []
    for v in hits:
        if all(abs(v["lat"] - k["lat"]) * 111_000 > metres or abs(v["lon"] - k["lon"]) * 67_000 > metres for k in kept):
            kept.append(v)
    return kept

def main():
    osm = json.load(open(DATA / "osm_venues.json"))
    venues, menus, unmatched = [], {}, []

    for row in csv.DictReader(open(DATA / "deals.csv")):
        brand = slug(row["name"])
        menus.setdefault(brand, {"brand": brand, "name": row["name"], "category": row["category"],
                                 "checked": date.today().isoformat(), "items": []})
        menus[brand]["items"].append({
            "name": row["dish"], "price": float(row["price_eur"]), "section": "Lunch",
            "lunch_deal": {"days": None, "from": None, "to": None},  # deal hours: fill when sourced
            "source": row["source"],
        })
        if any(v["brand"] == brand for v in venues):
            continue  # brand already placed (multiple deals for one brand)

        hits = []
        if row["match"]:
            hits = dedupe([v for v in osm if v["name"].lower().startswith(row["match"].lower())
                           and row["street_filter"].lower() in v["street"].lower()])
        base = {"brand": brand, "name": row["name"], "category": row["category"]}
        if hits:
            for v in hits:
                venues.append({**base, "id": slug(v["osm_id"]), "lat": v["lat"], "lon": v["lon"], "street": v["street"],
                               "website": v["website"], "hours": v["opening_hours"], "osm_id": v["osm_id"], "approx": False})
        elif row["lat"]:
            venues.append({**base, "id": f"{brand}-manual", "lat": float(row["lat"]), "lon": float(row["lon"]),
                           "street": "", "website": "", "hours": "", "osm_id": "", "approx": True})
        else:
            unmatched.append(row["name"])

    placed = {v["osm_id"] for v in venues}
    others = [{"name": v["name"], "lat": round(v["lat"], 5), "lon": round(v["lon"], 5), "amenity": v["amenity"]}
              for v in osm if v["osm_id"] not in placed and v["lat"]]

    OUT.mkdir(parents=True, exist_ok=True)
    json.dump(venues, open(OUT / "venues.json", "w"), indent=1, ensure_ascii=False)
    json.dump(menus, open(OUT / "menus.json", "w"), indent=1, ensure_ascii=False)
    json.dump(others, open(OUT / "unpriced.json", "w"), separators=(",", ":"), ensure_ascii=False)
    shutil.copy(DATA / "basemap.geojson", OUT / "basemap.geojson")
    print(f"{len(venues)} venues, {len(menus)} menus, {len(others)} unpriced; unmatched: {unmatched or 'none'}")

if __name__ == "__main__":
    main()
