import { reactive, computed, watch } from "vue";
import { track } from "./analytics";

const KEY = "grub-map:filters";
const slug = (s) => s.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
function load() {
  try { return JSON.parse(localStorage.getItem(KEY) || "{}"); } catch { return {}; }
}

export const state = reactive({
  venues: [],
  menus: {},
  max: 12,
  category: "",
  showUnpriced: false,
  selectedId: null,
  ...load(),
});

// Filter usage, counted anonymously so we learn what people look for.
watch(() => state.max, (m) => track(`filter/budget-${m}`, `Budget ≤ €${m}`));
watch(() => state.category, (c) => track(`filter/cuisine/${slug(c || "all")}`, `Cuisine: ${c || "All"}`));
watch(() => state.showUnpriced, (on) => on && track("filter/show-unpriced", "Show unpriced eateries"));

watch(() => [state.max, state.category, state.showUnpriced], () => {
  try {
    localStorage.setItem(KEY, JSON.stringify({ max: state.max, category: state.category, showUnpriced: state.showUnpriced }));
  } catch {}
});

export const lunchDeals = (menu) => (menu?.items ?? []).filter((i) => i.lunch_deal);
export const cheapestDeal = (menu) => Math.min(...lunchDeals(menu).map((i) => i.price));

// Venues joined with the cheapest lunch deal on their brand's menu.
export const rows = computed(() =>
  state.venues
    .map((v) => ({ ...v, price: cheapestDeal(state.menus[v.brand]) }))
    .filter((v) => Number.isFinite(v.price) && v.price <= state.max && (!state.category || v.category === state.category))
    .sort((a, b) => a.price - b.price || a.name.localeCompare(b.name)),
);

export const categories = computed(() => [...new Set(state.venues.map((v) => v.category))].sort());
export const selected = computed(() => rows.value.find((v) => v.id === state.selectedId) ?? null);

// Open a venue's panel. `from` says where the click came from ("list" or "map").
export function selectVenue(v, from) {
  state.selectedId = v.id;
  track(`venue/${v.brand}`, `${v.name} · ${from}`);
}

// Nothing matched the current filters: worth knowing which combos come up empty.
watch(() => rows.value.length, (n) => {
  if (n === 0 && state.venues.length) track(`empty/${state.max}/${slug(state.category || "all")}`, "No results for filters");
});

export const euro = (p) => "€" + (Number.isInteger(p) ? p : p.toFixed(2));
export const tier = (p) => (p <= 10 ? "p10" : "p12");
