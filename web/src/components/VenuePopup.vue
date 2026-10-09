<script setup>
import { computed } from "vue";
import { state, selected, lunchDeals, euro, tier, DIETS, dealWhen, openPanel } from "../lib/store";
import { useVenueActions } from "../lib/actions";

// The quick look shown on a pin: lunch deals and actions. The full menu opens in the side panel.
const deals = computed(() => (selected.value ? lunchDeals(state.menus[selected.value.brand]) : []));
const { directionsUrl, clicked, share, shareNote } = useVenueActions(selected);
</script>

<template>
  <div v-if="selected" class="pop">
    <div class="pop-name">{{ selected.name }}</div>
    <p class="meta">
      {{ selected.category }}<template v-if="selected.street"> · {{ selected.street }}</template>
      <template v-if="selected.approx"> · location approximate</template>
    </p>
    <p v-if="selected.diets.length || selected.student" class="tags">
      <span v-if="selected.student" class="tag tag-student">Student deal</span>
      <span v-for="d in selected.diets" :key="d" class="tag">{{ DIETS[d] }}</span>
    </p>
    <ul class="pop-deals">
      <li v-for="d in deals" :key="d.id">
        <div>
          <div class="n">{{ d.name }}</div>
          <div class="meta">{{ dealWhen(d) }}</div>
        </div>
        <span class="price" :class="tier(d.price)">{{ euro(d.price) }}</span>
      </li>
    </ul>
    <div class="actions">
      <a class="directions" :href="directionsUrl" target="_blank" rel="noopener" @click="clicked('directions')">Walk there ↗</a>
      <button type="button" class="share" @click="share">Share</button>
      <!-- v-show, not v-if: removing the clicked button mid-click makes Leaflet treat it as a map click and close the popup -->
      <button v-show="!state.panelOpen" type="button" class="inline-link" @click="openPanel">Full menu →</button>
    </div>
    <p v-if="shareNote" class="meta share-note" role="status">{{ shareNote }}</p>
  </div>
</template>
