<script setup>
import { computed } from "vue";
import { state, selected, lunchDeals, euro, tier } from "../lib/store";

const menu = computed(() => (selected.value ? state.menus[selected.value.brand] : null));
const deals = computed(() => lunchDeals(menu.value));
// Everything that isn't a lunch deal, grouped by menu section.
const sections = computed(() => {
  const groups = {};
  for (const item of menu.value?.items ?? []) {
    if (item.lunch_deal) continue;
    (groups[item.section || "Menu"] ??= []).push(item);
  }
  return Object.entries(groups);
});
const dealWhen = (d) => {
  const { days, from, to } = d.lunch_deal;
  if (!days && !from) return "Lunch hours not confirmed";
  return [days, from && to ? `${from}–${to}` : ""].filter(Boolean).join(" · ");
};
const host = (url) => { try { return new URL(url).hostname.replace(/^www\./, ""); } catch { return url; } };
</script>

<template>
  <div v-if="selected" class="detail">
    <button type="button" class="back" @click="state.selectedId = null">← All spots</button>
    <h2>{{ selected.name }}</h2>
    <p class="meta">
      {{ selected.category }}<template v-if="selected.street"> · {{ selected.street }}</template>
      <template v-if="selected.approx"> · location approximate</template>
    </p>
    <p v-if="selected.hours" class="meta">Open: {{ selected.hours }}</p>
    <p v-if="selected.website" class="meta"><a :href="selected.website" target="_blank" rel="noopener">{{ host(selected.website) }}</a></p>

    <h3>Lunch deal</h3>
    <ul class="menu">
      <li v-for="d in deals" :key="d.name" class="deal">
        <div>
          <div class="n">{{ d.name }}</div>
          <div class="meta">{{ dealWhen(d) }} · <a :href="d.source" target="_blank" rel="noopener">source: {{ host(d.source) }}</a></div>
        </div>
        <span class="price" :class="tier(d.price)">{{ euro(d.price) }}</span>
      </li>
    </ul>

    <template v-for="[section, items] in sections" :key="section">
      <h3>{{ section }}</h3>
      <ul class="menu">
        <li v-for="i in items" :key="i.name">
          <div class="n">{{ i.name }}</div>
          <span class="menu-price">{{ euro(i.price) }}</span>
        </li>
      </ul>
    </template>
    <p v-if="!sections.length" class="note">Full menu not added yet.</p>
  </div>
</template>
