"""Fetch a lightweight vector basemap (streets, River Liffey, parks) from OSM so the map needs no tile server."""
import json, urllib.request, urllib.parse
from pathlib import Path

DATA = Path(__file__).parent / "data"
from fetch_osm import BBOX

QUERY = f"""
[out:json][timeout:90];
(
  way["highway"~"^(primary|secondary|tertiary|residential|pedestrian|unclassified|living_street)$"]{BBOX};
  way["waterway"="river"]{BBOX};
  way["natural"="water"]{BBOX};
  way["leisure"="park"]{BBOX};
);
out geom tags;
"""

def kind(t):
    if "highway" in t:
        h = t["highway"]
        return "major" if h in ("primary", "secondary") else "pedestrian" if h == "pedestrian" else "minor"
    if t.get("leisure") == "park":
        return "park"
    return "water"

def main():
    req = urllib.request.Request(
        "https://overpass-api.de/api/interpreter",
        data=urllib.parse.urlencode({"data": QUERY}).encode(),
        headers={"User-Agent": "grub-map/0.1", "Accept": "application/json"},
    )
    feats = []
    for el in json.load(urllib.request.urlopen(req, timeout=120))["elements"]:
        if "geometry" not in el:
            continue
        coords = [[round(p["lon"], 5), round(p["lat"], 5)] for p in el["geometry"]]
        k = kind(el["tags"])
        closed = coords[0] == coords[-1] and k in ("park", "water")
        feats.append({
            "type": "Feature",
            "properties": {"k": k, "n": el["tags"].get("name", "") if k == "major" else ""},
            "geometry": {"type": "Polygon", "coordinates": [coords]} if closed
                        else {"type": "LineString", "coordinates": coords},
        })
    json.dump({"type": "FeatureCollection", "features": feats}, open(DATA / "basemap.geojson", "w"), separators=(",", ":"))
    print(f"saved {len(feats)} basemap features")

if __name__ == "__main__":
    main()
