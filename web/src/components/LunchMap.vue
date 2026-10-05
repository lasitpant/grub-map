<script setup>
import { onMounted, onBeforeUnmount, ref, watch } from "vue";
import L from "leaflet";
import { state, rows, euro, tier, selectVenue } from "../lib/store";
import { getBasemap, getUnpriced } from "../lib/api";

const el = ref(null);
let map, dealLayer, unpricedLayer;
const markers = new Map();

const WEIGHT = { major: 6, minor: 3, pedestrian: 3, water: 1, park: 0 };
const ORDER = ["park", "water", "minor", "pedestrian", "major"];

async function drawBasemap() {
  const tiles = import.meta.env.VITE_TILE_URL;
  if (tiles) {
    L.tileLayer(tiles, { maxZoom: 19 }).addTo(map);
    return;
  }
  const { features = [] } = await getBasemap();
  for (const k of ORDER) {
    L.geoJSON({ type: "FeatureCollection", features: features.filter((f) => f.properties.k === k) }, {
      interactive: false,
      style: () => ({ className: `bm-${k}`, weight: WEIGHT[k], opacity: 1, fillOpacity: 1, lineCap: "round" }),
    }).addTo(map);
  }
}

function drawDeals() {
  dealLayer.clearLayers();
  markers.clear();
  for (const v of rows.value) {
    const cls = ["pin", tier(v.price), v.approx && "approx", v.id === state.selectedId && "hl"].filter(Boolean).join(" ");
    const m = L.marker([v.lat, v.lon], {
      icon: L.divIcon({ className: "", html: `<span class="${cls}">${euro(v.price)}</span>`, iconSize: null }),
      title: v.name,
      riseOnHover: true,
      zIndexOffset: v.id === state.selectedId ? 1000 : 0,
    }).on("click", () => selectVenue(v, "map"));
    m.addTo(dealLayer);
    markers.set(v.id, m);
  }
}

async function toggleUnpriced(on) {
  if (!on) return unpricedLayer?.remove();
  if (!unpricedLayer) {
    const dot = getComputedStyle(document.documentElement).getPropertyValue("--dot").trim();
    unpricedLayer = L.layerGroup((await getUnpriced()).map((u) =>
      L.circleMarker([u.lat, u.lon], { radius: 3, stroke: false, fillColor: dot, fillOpacity: 0.7 })
        .bindTooltip(`${u.name} · no price yet`)));
  }
  if (state.showUnpriced) unpricedLayer.addTo(map);
}

onMounted(async () => {
  map = L.map(el.value, { minZoom: 13, maxZoom: 19 }).setView([53.3455, -6.262], 15);
  map.setMaxBounds([[53.325, -6.3], [53.366, -6.22]]);
  map.attributionControl.setPrefix(false)
    .addAttribution('© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors');
  dealLayer = L.layerGroup().addTo(map);
  await drawBasemap();
  drawDeals();
  toggleUnpriced(state.showUnpriced);
});
onBeforeUnmount(() => map?.remove());

watch(rows, () => map && drawDeals());
watch(() => state.showUnpriced, (on) => map && toggleUnpriced(on));
watch(() => state.selectedId, (id) => {
  if (!map) return;
  drawDeals();
  const m = markers.get(id);
  if (m) map.setView(m.getLatLng(), Math.max(map.getZoom(), 17));
});
</script>

<template>
  <div ref="el" class="map" aria-label="Map of lunch spots"></div>
</template>
