<script setup>
import { rows, euro, tier, selectVenue } from "../lib/store";
</script>

<template>
  <div class="summary">
    <span><b>{{ rows.length }}</b> spots</span>
    <span class="key"><i class="sw" style="background: var(--ten)"></i>≤ €10</span>
    <span class="key"><i class="sw" style="background: var(--twelve)"></i>€10–12</span>
    <span class="key"><i class="sw sw-approx"></i>approx. location</span>
  </div>
  <ul>
    <li v-for="v in rows" :key="v.id">
      <button type="button" class="item" @click="selectVenue(v, 'list')">
        <span class="n">{{ v.name }}</span>
        <span class="price" :class="tier(v.price)">{{ euro(v.price) }}</span>
        <span class="meta">{{ v.category }}<template v-if="v.street"> · {{ v.street }}</template></span>
      </button>
    </li>
  </ul>
  <p class="note">
    Proof of concept. Prices come from 2024–2026 published guides and may have changed, so check before you go.
    Locations, opening hours and websites come from OpenStreetMap. Dashed pins were placed by street address.
  </p>
  <p class="note">
    Privacy: no cookies, no accounts, no personal data. Restaurants can't pay to be listed or ranked.
    We count visits and clicks anonymously with <a href="https://www.goatcounter.com" target="_blank" rel="noopener">GoatCounter</a>.
  </p>
</template>
