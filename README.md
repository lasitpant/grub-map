# Grub Map

Dublin lunches under €10 and €12, for office workers and students. Real prices, sourced and dated. Restaurants can't pay to be listed or ranked.

```
pipeline/   Python: fetch OSM venues + basemap, merge curated deals, export JSON
web/        Vue 3 + Vite + Leaflet frontend
```

## Run
```
python3 pipeline/export.py      # writes web/public/data/*.json
cd web && npm install && npm run dev
```
Refresh OSM data: `python3 pipeline/fetch_osm.py` and `python3 pipeline/fetch_basemap.py`.

## Data model
- `venues.json`: one row per location, linked to a menu by `brand` (chains share a menu).
- `menus.json`: `{ brand: { items: [{ name, price, section, lunch_deal, source }] } }`.
  `lunch_deal` is `null` for regular menu items, or `{ days, from, to }` for lunch offers.

The frontend reads data through `web/src/lib/api.js`. Set `VITE_API_BASE` (see `web/.env.example`)
to switch from static JSON to a backend serving `/venues`, `/venues/unpriced`, `/menus`, `/menus/:brand`.

## Analytics
Anonymous, cookieless counting with [GoatCounter](https://www.goatcounter.com). Set `VITE_GOATCOUNTER_CODE`
(see `web/.env.example`); leave it unset to disable. No cookies, no stored IPs, nothing per-person.

| Event path | Counted when |
|---|---|
| `/` (page view) | Someone opens the site (GoatCounter also gives referrer, country, browser, screen size) |
| `venue/<brand>` | A venue is opened; the title says whether from the `list` or the `map` |
| `directions/<brand>` | "Walk there in Google Maps" is clicked |
| `website/<brand>`, `source/<brand>` | The venue website or a price source is opened |
| `filter/budget-10`, `filter/budget-12` | The budget toggle is changed |
| `filter/cuisine/<name>`, `filter/show-unpriced` | Cuisine filter or unpriced layer is used |
| `empty/<budget>/<cuisine>` | A filter combination returns no spots |

## Licence
- **Code:** MIT, see [LICENSE](LICENSE).
- **OpenStreetMap data** (`pipeline/data/osm_venues.json`, `pipeline/data/basemap.geojson`, and the files derived from them in `web/public/data/`):
  © OpenStreetMap contributors, available under the [Open Database License (ODbL)](https://www.openstreetmap.org/copyright).
  Any reuse must keep this attribution and licence.
- **Lunch prices** (`pipeline/data/deals.csv`): short factual entries (dish, price, link to the source). Check the linked source before relying on a price.
