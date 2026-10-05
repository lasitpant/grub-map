// Data access. Today it reads static JSON exported by pipeline/export.py.
// Set VITE_API_BASE to point at a backend; the REST routes below mirror the JSON shapes.
const API = import.meta.env.VITE_API_BASE;
const STATIC = `${import.meta.env.BASE_URL}data`;

const cache = new Map();
async function get(url) {
  if (!cache.has(url)) {
    cache.set(url, fetch(url).then((r) => {
      if (!r.ok) throw new Error(`Couldn't load ${url} (${r.status})`);
      return r.json();
    }));
  }
  return cache.get(url);
}

export const getVenues = () => get(API ? `${API}/venues` : `${STATIC}/venues.json`);

// Menus keyed by brand, so all branches of a chain share one menu.
export async function getMenus() {
  return get(API ? `${API}/menus` : `${STATIC}/menus.json`);
}
export async function getMenu(brand) {
  if (API) return get(`${API}/menus/${encodeURIComponent(brand)}`);
  return (await getMenus())[brand] ?? null;
}

export const getUnpriced = () => get(API ? `${API}/venues/unpriced` : `${STATIC}/unpriced.json`);
export const getBasemap = () => get(`${STATIC}/basemap.geojson`);
