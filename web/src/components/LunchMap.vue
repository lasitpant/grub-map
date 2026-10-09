<script setup>
import { onMounted, onBeforeUnmount, ref, watch } from "vue";
import L from "leaflet";
import { state, rows, selected, euro, tier, selectVenue } from "../lib/store";
import { getBasemap, getUnpriced } from "../lib/api";
import VenuePopup from "./VenuePopup.vue";

const el = ref(null);
let map, dealLayer, unpricedLayer, popup;
const markers = new Map();
// One shared popup; VenuePopup renders into this element through a Teleport.
const popupEl = document.createElement("div");

const WEIGHT = { major: 6, minor: 3, pedestrian: 3, water: 1, park: 0 };
const ORDER = ["park", "water", "minor", "pedestrian", "major"];

// OpenFreeMap vector tiles (OSM data: street names, buildings, landmarks), following the system light/dark theme.
// MapLibre draws them inside Leaflet; it's loaded on demand so the pins don't wait for it.
const STYLES = { light: "https://tiles.openfreemap.org/styles/liberty", dark: "https://tiles.openfreemap.org/styles/dark" };
const darkQuery = matchMedia("(prefers-color-scheme: dark)");
const styleUrl = () => STYLES[darkQuery.matches ? "dark" : "light"];

async function drawBasemap() {
  const tiles = import.meta.env.VITE_TILE_URL;
  if (tiles && tiles !== "vector") {
    L.tileLayer(tiles, { maxZoom: 19 }).addTo(map);
    return;
  }
  if (!tiles) {
    const [{ setWorkerUrl }, { maplibreGL }, { default: workerUrl }] = await Promise.all([
      import("maplibre-gl"),
      import("@maplibre/maplibre-gl-leaflet"),
      import("maplibre-gl/dist/maplibre-gl-worker.mjs?worker&url"), // bundled by Vite; MapLibre can't locate it itself
      import("maplibre-gl/dist/maplibre-gl.css"),
    ]);
    setWorkerUrl(workerUrl);
    const layer = maplibreGL({
      style: styleUrl(),
      attribution: '<a href="https://openfreemap.org" target="_blank">OpenFreeMap</a> © <a href="https://www.openmaptiles.org/" target="_blank">OpenMapTiles</a>',
    }).addTo(map);
    darkQuery.onchange = () => layer.getMaplibreMap().setStyle(styleUrl());
    return;
  }
  // "vector": the bundled OSM basemap, so the map works with no tile server.
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
    }).on("click", () => (v.id === state.selectedId ? showPopup(v.id) : selectVenue(v, "map")));
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
  popup = L.popup({ offset: [0, -8], minWidth: 240, maxWidth: 280, autoPanPadding: [16, 16] }).setContent(popupEl);
  // Closing the popup (× or a click on the map) clears the focus, unless the full menu is open in the side panel.
  popup.on("remove", () => {
    if (!state.panelOpen && popup.venueId === state.selectedId) state.selectedId = null;
  });
  drawBasemap();
  drawDeals();
  toggleUnpriced(state.showUnpriced);
  showPopup(state.selectedId);
});
onBeforeUnmount(() => {
  darkQuery.onchange = null;
  map?.remove();
});

watch(rows, () => map && drawDeals());
watch(() => state.showUnpriced, (on) => map && toggleUnpriced(on));
function showPopup(id) {
  const v = selected.value;
  if (!v) return popup.close();
  popup.venueId = id;
  if (map.getZoom() < 17) map.setView([v.lat, v.lon], 17);
  popup.setLatLng([v.lat, v.lon]); // if already open, this re-measures for the new venue and pans it into view
  if (!popup.isOpen()) popup.openOn(map);
}

// Runs after the DOM update, so the popup measures the new venue's content.
watch(() => state.selectedId, (id) => {
  if (!map) return;
  drawDeals();
  showPopup(id);
}, { flush: "post" });
</script>

<template>
  <div ref="el" class="map" aria-label="Map of lunch spots"></div>
  <Teleport :to="popupEl"><VenuePopup /></Teleport>
</template>
