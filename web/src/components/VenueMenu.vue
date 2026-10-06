<script setup>
import { computed, ref } from "vue";
import { state, selected, lunchDeals, euro, tier, DIETS, shortDate } from "../lib/store";
import { track } from "../lib/analytics";
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
const dealWhen = (d) => {
  const { days, from, to } = d.lunch_deal;
  if (!days && !from) return "Lunch hours not confirmed";
  return [days, from && to ? `${from}–${to}` : ""].filter(Boolean).join(" · ");
};
const CHECKED_HOW = { guide: "Price from", menu: "Price from menu at", visit: "Price checked in person, see" };

// Walking directions in Google Maps (opens the app on phones if installed).
// Hand-placed venues use a name search instead, since their pin is only approximate.
const directionsUrl = computed(() => {
  const v = selected.value;
  if (!v) return "";
  const base = "https://www.google.com/maps/dir/?api=1&travelmode=walking&destination=";
  return base + encodeURIComponent(v.approx ? `${v.name}, Dublin` : `${v.lat},${v.lon}`);
});
const clicked = (kind) => track(`${kind}/${selected.value.brand}`, `${selected.value.name} · ${kind}`);

// Share this venue: the phone's share sheet where available, otherwise copy the link.
const shareNote = ref("");
async function share() {
  const v = selected.value;
  const url = `${location.origin}${location.pathname}#${v.id}`;
  const text = `${v.name}: lunch from ${euro(v.price)} on Grub Map`;
  clicked("share");
  try {
    if (navigator.share) return await navigator.share({ title: v.name, text, url });
    await navigator.clipboard.writeText(url);
    shareNote.value = "Link copied";
  } catch (e) {
    if (e?.name !== "AbortError") shareNote.value = url; // clipboard blocked: show the link to copy by hand
  }
  setTimeout(() => (shareNote.value = ""), 4000);
}

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
