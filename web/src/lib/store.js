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
  feedback: {},       // item id -> { still, changed, last_still, last_changed } from the API
  max: 12,
  category: "",
  diet: "",           // "", vegetarian, vegan, halal, gluten_free
  studentOnly: false,
  showUnpriced: false,
  selectedId: null,
  showAbout: false,
  ...load(),
});

// Filter usage, counted anonymously so we learn what people look for.
watch(() => state.max, (m) => track(`filter/budget-${m}`, `Budget ≤ €${m}`));
watch(() => state.category, (c) => track(`filter/cuisine/${slug(c || "all")}`, `Cuisine: ${c || "All"}`));
watch(() => state.diet, (d) => d && track(`filter/diet/${d}`, `Diet: ${DIETS[d]}`));
watch(() => state.studentOnly, (on) => on && track("filter/student-discount", "Student discount only"));
watch(() => state.showUnpriced, (on) => on && track("filter/show-unpriced", "Show unpriced eateries"));

watch(() => [state.max, state.category, state.diet, state.studentOnly, state.showUnpriced], () => {
  const { max, category, diet, studentOnly, showUnpriced } = state;
  try { localStorage.setItem(KEY, JSON.stringify({ max, category, diet, studentOnly, showUnpriced })); } catch {}
});

export const DIETS = { vegetarian: "Veggie", vegan: "Vegan", halal: "Halal", gluten_free: "Gluten-free" };

export const lunchDeals = (menu) => (menu?.items ?? []).filter((i) => i.lunch_deal != null);
export const cheapestDeal = (menu) => Math.min(...lunchDeals(menu).map((i) => i.price));
// Diet options at a venue: venue-level tags from OpenStreetMap plus dish-level tags from our data.
export const venueDiets = (menu) => [...new Set([...(menu?.diet ?? []), ...lunchDeals(menu).flatMap((i) => i.diet ?? [])])];

// Every priced venue, joined with its menu facts. Shared links open from this, even if filters hide the venue.
const priced = computed(() =>
  state.venues
    .map((v) => {
      const menu = state.menus[v.brand];
      return { ...v, price: cheapestDeal(menu), diets: venueDiets(menu), student: menu?.student_discount ?? null };
    })
    .filter((v) => Number.isFinite(v.price)),
);

export const rows = computed(() =>
  priced.value
    .filter((v) => v.price <= state.max
      && (!state.category || v.category === state.category)
      && (!state.diet || v.diets.includes(state.diet))
      && (!state.studentOnly || v.student))
    .sort((a, b) => a.price - b.price || a.name.localeCompare(b.name)),
);

export const categories = computed(() => [...new Set(state.venues.map((v) => v.category))].sort());
export const selected = computed(() => priced.value.find((v) => v.id === state.selectedId) ?? null);

// Open a venue's panel. `from` says where the click came from ("list", "map" or "link").
export function selectVenue(v, from) {
  state.selectedId = v.id;
  track(`venue/${v.brand}`, `${v.name} · ${from}`);
}

// Keep the address bar in sync so any open venue (or the About page) can be shared as grubmap…/#id.
watch(() => [state.selectedId, state.showAbout], ([id, about]) => {
  const target = id || (about ? "about" : "");
  if (location.hash.slice(1) !== target) history.replaceState(null, "", target ? `#${target}` : location.pathname + location.search);
});
watch(() => state.showAbout, (on) => {
  if (!on) return;
  state.selectedId = null;
  track("about", "About page");
});
watch(() => state.selectedId, (id) => id && (state.showAbout = false));
export function openFromHash() {
  const id = decodeURIComponent(location.hash.slice(1));
  if (id === "about") return void (state.showAbout = true);
  const v = id && priced.value.find((x) => x.id === id);
  if (v && state.selectedId !== id) selectVenue(v, "link");
}

// Nothing matched the current filters: worth knowing which combos come up empty.
watch(() => rows.value.length, (n) => {
  if (n === 0 && state.venues.length) {
    track(`empty/${state.max}/${slug(state.category || "all")}/${state.diet || "any"}`, "No results for filters");
  }
});

export const euro = (p) => "€" + (Number.isInteger(p) ? p : p.toFixed(2));
export const tier = (p) => (p <= 10 ? "p10" : "p12");
export const shortDate = (iso) => new Date(iso).toLocaleDateString("en-IE", { day: "numeric", month: "short", year: "numeric" });
export function ago(iso) {
  const days = Math.floor((Date.now() - new Date(iso)) / 86_400_000);
  return days <= 0 ? "today" : days === 1 ? "yesterday" : `${days} days ago`;
}
