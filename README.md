# Grub Map

Dublin lunches under €10 and €12, for office workers and students. Real prices, sourced and dated. Restaurants can't pay to be listed or ranked.

```
pipeline/   Python: fetch OSM venues + basemap, merge curated deals, export JSON
web/        Vue 3 + Vite + Leaflet frontend
backend/    FastAPI + SQLite: anonymous "still this price?" votes
```

## Run
```
python3 pipeline/export.py      # writes web/public/data/*.json
cd web && npm install && npm run dev
cd backend && uv run grub-map-api   # optional: vote API on :8000 (web/.env.development points at it)
cd backend && uv run pytest         # backend tests
```
Refresh OSM data: `python3 pipeline/fetch_osm.py` and `python3 pipeline/fetch_basemap.py`.

The map uses [OpenFreeMap](https://openfreemap.org) vector tiles (free, no API key). Set `VITE_TILE_URL=vector` to use the bundled
lightweight basemap from `fetch_basemap.py` instead (see `web/.env.example`).

## Adding deals
Edit `pipeline/data/deals.csv`, then run `python3 pipeline/export.py`. Columns:

| Column | Meaning |
|---|---|
| `name`, `dish`, `price_eur`, `category` | The deal |
| `match`, `street_filter` | Name prefix (and optional street) to find the venue in OpenStreetMap; chains get one pin per branch |
| `lat`, `lon` | Only when the venue isn't in OSM (shown as an approximate pin) |
| `diet` | Dish-level tags, `;`-separated: `vegetarian`, `vegan`, `halal`, `gluten_free`. Only when certain. Venue-level options come from OSM `diet:*` tags automatically |
| `student_discount`, `student_source` | e.g. `10% off with student ID` and where that's stated |
| `checked`, `checked_how` | Date the price was collected and how: `guide` (an article), `menu` (venue's own menu), `visit` (seen in person) |
| `source` | Link to where the price came from |

Shareable links: every venue has a readable id (`aobaba`, `boojum-smithfield`) and opens directly at `/#<id>`.

## Data model
- `venues.json`: one row per location, linked to a menu by `brand` (chains share a menu).
- `menus.json`: `{ brand: { items: [{ name, price, section, lunch_deal, source }] } }`.
  `lunch_deal` is `null` for regular menu items, or `{ days, from, to }` for lunch offers.

Venues and menus are static JSON. Live features go through `web/src/lib/api.js` to the backend at
`VITE_API_BASE`; when it's unset (as in production until the API is deployed) the vote buttons are hidden.

## Backend (votes)
- `GET /api/feedback`: per deal, counts of "still this price" and "price changed" in the last 60 days.
- `POST /api/feedback` `{item_id, kind: "still"|"changed", price?}`: rate-limited to 30/hour per connection.
- `GET /api/admin/price-reports`: "price changed" reports to review. Needs `Authorization: Bearer $ADMIN_TOKEN`.

Privacy: the database stores only the deal id, vote type, optional price and time. No IPs, user agents or cookies.
Rate limiting uses an in-memory hash of the IP with a salt that rotates daily, never written to disk.

Settings (environment variables): `DATABASE_PATH`, `MENUS_PATH`, `ALLOWED_ORIGINS` (comma-separated site URLs), `ADMIN_TOKEN`.

## Analytics
Anonymous, cookieless counting with [GoatCounter](https://www.goatcounter.com). Set `VITE_GOATCOUNTER_CODE`
(see `web/.env.example`); leave it unset to disable. No cookies, no stored IPs, nothing per-person.

| Event path | Counted when |
|---|---|
| `/` (page view) | Someone opens the site (GoatCounter also gives referrer, country, browser, screen size) |
| `venue/<brand>` | A venue is opened; the title says whether from the `list` or the `map` |
| `directions/<brand>` | "Walk there in Google Maps" is clicked |
| `website/<brand>`, `source/<brand>` | The venue website or a price source is opened |
| `share/<brand>` | The Share button is used |
| `price-still/<brand>`, `price-changed/<brand>` | Someone confirms or disputes a price |
| `filter/budget-10`, `filter/budget-12` | The budget toggle is changed |
| `filter/cuisine/<name>`, `filter/diet/<diet>` | Cuisine or diet filter is used |
| `filter/student-discount`, `filter/show-unpriced` | Student-discount filter or unpriced layer is switched on |
| `empty/<budget>/<cuisine>/<diet>` | A filter combination returns no spots |

## Licence
- **Code:** MIT, see [LICENSE](LICENSE).
- **OpenStreetMap data** (`pipeline/data/osm_venues.json`, `pipeline/data/basemap.geojson`, and the files derived from them in `web/public/data/`):
  © OpenStreetMap contributors, available under the [Open Database License (ODbL)](https://www.openstreetmap.org/copyright).
  Any reuse must keep this attribution and licence.
- **Lunch prices** (`pipeline/data/deals.csv`): short factual entries (dish, price, link to the source). Check the linked source before relying on a price.
