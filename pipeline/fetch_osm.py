"""Fetch Dublin city-centre eateries from OpenStreetMap (Overpass API). Free, no key."""
import json, urllib.request, urllib.parse
from pathlib import Path

DATA = Path(__file__).parent / "data"

BBOX = (53.3330, -6.2850, 53.3580, -6.2350)  # south, west, north, east: canals-ish city centre
QUERY = f"""
[out:json][timeout:60];
nwr["amenity"~"^(cafe|restaurant|fast_food|pub)$"]["name"]{BBOX};
out center tags;
"""

def main():
    req = urllib.request.Request(
        "https://overpass-api.de/api/interpreter",
        data=urllib.parse.urlencode({"data": QUERY}).encode(),
        headers={"User-Agent": "grub-map/0.1", "Accept": "application/json"},
    )
    raw = json.load(urllib.request.urlopen(req, timeout=90))["elements"]
    venues = []
    for el in raw:
        lat = el.get("lat") or el.get("center", {}).get("lat")
        lon = el.get("lon") or el.get("center", {}).get("lon")
        t = el["tags"]
        venues.append({
            "osm_id": f'{el["type"]}/{el["id"]}', "name": t["name"], "lat": lat, "lon": lon,
            "amenity": t.get("amenity"), "cuisine": t.get("cuisine", ""),
            "street": t.get("addr:street", ""), "website": t.get("website") or t.get("contact:website", ""),
            "opening_hours": t.get("opening_hours", ""),
        })
    json.dump(venues, open(DATA / "osm_venues.json", "w"), indent=1, ensure_ascii=False)
    print(f"saved {len(venues)} venues")

if __name__ == "__main__":
    main()
