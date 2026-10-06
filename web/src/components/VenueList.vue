<script setup>
import { state, rows, euro, tier, selectVenue, DIETS } from "../lib/store";
</script>

<template>
  <p class="intro">
    Real lunch deals with the price and its source. Restaurants never pay to be here.
    <button type="button" class="inline-link" @click="state.showAbout = true">Why Grub Map?</button>
  </p>
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
        <span v-if="v.diets.length || v.student" class="tags">
          <span v-if="v.student" class="tag tag-student">Student deal</span>
          <span v-for="d in v.diets" :key="d" class="tag">{{ DIETS[d] }}</span>
        </span>
      </button>
    </li>
  </ul>
  <p class="note">
    Proof of concept. Prices come from 2024–2026 published guides and may have changed, so check before you go.
    Locations, opening hours and websites come from OpenStreetMap. Dashed pins were placed by street address.
  </p>
  <p class="note">
    Privacy: no cookies, no accounts, no personal data. We count visits and clicks anonymously with
    <a href="https://www.goatcounter.com" target="_blank" rel="noopener">GoatCounter</a>.
    <button type="button" class="inline-link" @click="state.showAbout = true">About Grub Map</button>
  </p>
</template>
