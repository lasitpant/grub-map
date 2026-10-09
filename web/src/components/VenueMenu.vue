<script setup>
import { computed } from "vue";
import { state, selected, lunchDeals, euro, tier, DIETS, shortDate, dealWhen } from "../lib/store";
import { host, useVenueActions } from "../lib/actions";
import DealFeedback from "./DealFeedback.vue";

const menu = computed(() => (selected.value ? state.menus[selected.value.brand] : null));
const deals = computed(() => lunchDeals(menu.value));
// Everything that isn't a lunch deal, grouped by menu section.
const sections = computed(() => {
  const groups = {};
  for (const item of menu.value?.items ?? []) {
    if (item.lunch_deal != null) continue;
    (groups[item.section || "Menu"] ??= []).push(item);
  }
  return Object.entries(groups);
});
const CHECKED_HOW = { guide: "Price from", menu: "Price from menu at", visit: "Price checked in person, see" };

const { directionsUrl, clicked, share, shareNote } = useVenueActions(selected);
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
    <p v-if="selected.website" class="meta">
      <a :href="selected.website" target="_blank" rel="noopener" @click="clicked('website')">{{ host(selected.website) }}</a>
    </p>
    <p v-if="menu?.diet.length" class="tags">
      <span v-for="d in menu.diet" :key="d" class="tag">{{ DIETS[d] }} options</span>
    </p>
    <div class="actions">
      <a class="directions" :href="directionsUrl" target="_blank" rel="noopener" @click="clicked('directions')">Walk there in Google Maps ↗</a>
      <button type="button" class="share" @click="share">Share</button>
      <span v-if="shareNote" class="meta share-note" role="status">{{ shareNote }}</span>
    </div>

    <div v-if="menu?.student_discount" class="student">
      <b>Student discount:</b> {{ menu.student_discount.text }}
      <a v-if="menu.student_discount.source" :href="menu.student_discount.source" target="_blank" rel="noopener"
         class="meta" @click="clicked('source')">source: {{ host(menu.student_discount.source) }}</a>
    </div>

    <h3>Lunch deal</h3>
    <ul class="menu">
      <li v-for="d in deals" :key="d.id" class="deal">
        <div class="deal-head">
          <div>
            <div class="n">{{ d.name }}</div>
            <div v-if="d.diet?.length" class="tags">
              <span v-for="t in d.diet" :key="t" class="tag">{{ DIETS[t] }}</span>
            </div>
            <div class="meta">{{ dealWhen(d) }}</div>
            <div class="meta">
              {{ CHECKED_HOW[d.checked?.how] ?? "Price from" }}
              <a :href="d.source" target="_blank" rel="noopener" @click="clicked('source')">{{ host(d.source) }}</a><template
                v-if="d.checked?.date">, collected {{ shortDate(d.checked.date) }}</template>
            </div>
          </div>
          <span class="price" :class="tier(d.price)">{{ euro(d.price) }}</span>
        </div>
        <DealFeedback :deal="d" :venue="selected" />
      </li>
    </ul>

    <template v-for="[section, items] in sections" :key="section">
      <h3>{{ section }}</h3>
      <ul class="menu">
        <li v-for="i in items" :key="i.id ?? i.name">
          <div class="n">{{ i.name }}</div>
          <span class="menu-price">{{ euro(i.price) }}</span>
        </li>
      </ul>
    </template>
    <p v-if="!sections.length" class="note">
      Full menu not added yet.
      <a v-if="selected.website" :href="selected.website" target="_blank" rel="noopener" @click="clicked('website')">See their website</a>
    </p>
  </div>
</template>
