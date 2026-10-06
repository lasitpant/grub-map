// Data access. Venues and menus are static JSON exported by pipeline/export.py.
// Live features ("still this price?" votes) call the backend at VITE_API_BASE; they're hidden when it's unset.
const STATIC = `${import.meta.env.BASE_URL}data`;
export const API = import.meta.env.VITE_API_BASE || "";

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

export const getVenues = () => get(`${STATIC}/venues.json`);
export const getMenus = () => get(`${STATIC}/menus.json`); // keyed by brand: branches of a chain share one menu
export const getUnpriced = () => get(`${STATIC}/unpriced.json`);
export const getBasemap = () => get(`${STATIC}/basemap.geojson`);

export async function getFeedback() {
  if (!API) return {};
  const r = await fetch(`${API}/feedback`);
  return r.ok ? r.json() : {};
}

// kind: "still" | "changed"; price only with "changed".
export async function sendFeedback(itemId, kind, price) {
  const r = await fetch(`${API}/feedback`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ item_id: itemId, kind, price }),
  });
  if (r.status === 429) throw new Error("Too many votes from this connection. Try again later.");
  if (!r.ok) throw new Error("Couldn't send that. Try again in a moment.");
}
