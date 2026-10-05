import { reactive, computed, watch } from "vue";

const KEY = "grub-map:filters";
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

export const euro = (p) => "€" + (Number.isInteger(p) ? p : p.toFixed(2));
export const tier = (p) => (p <= 10 ? "p10" : "p12");
