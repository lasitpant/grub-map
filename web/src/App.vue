<script setup>
import { onMounted, ref } from "vue";
import { getVenues, getMenus, getFeedback } from "./lib/api";
import { state, categories, DIETS, openFromHash } from "./lib/store";
import LunchMap from "./components/LunchMap.vue";
import VenueList from "./components/VenueList.vue";
import VenueMenu from "./components/VenueMenu.vue";
import AboutPanel from "./components/AboutPanel.vue";

const error = ref("");
// Votes are optional extras: load them in the background and never block the map.
getFeedback().then((f) => (state.feedback = f)).catch(() => {});
onMounted(async () => {
  try {
    [state.venues, state.menus] = await Promise.all([getVenues(), getMenus()]);
    openFromHash();
    window.addEventListener("hashchange", openFromHash);
  } catch (e) {
    error.value = `${e.message}. Run pipeline/export.py, then reload.`;
  }
});
</script>

<template>
  <div class="app">
    <header>
      <h1>Grub Map <small>Dublin lunches under €10 and €12</small></h1>
      <button type="button" class="about-link" :aria-pressed="state.showAbout" @click="state.showAbout = !state.showAbout">About</button>
      <div class="controls">
        <div class="seg" role="group" aria-label="Budget">
          <button v-for="m in [10, 12]" :key="m" type="button" :aria-pressed="state.max === m" @click="state.max = m">
            ≤ €{{ m }}
          </button>
        </div>
        <select id="cat" v-model="state.category" aria-label="Cuisine">
          <option value="">All cuisines</option>
          <option v-for="c in categories" :key="c" :value="c">{{ c }}</option>
        </select>
        <select id="diet" v-model="state.diet" aria-label="Diet">
          <option value="">Any diet</option>
          <option v-for="(label, key) in DIETS" :key="key" :value="key">{{ label }}</option>
        </select>
        <label class="toggle"><input id="student" v-model="state.studentOnly" type="checkbox" /> Student discount</label>
        <label class="toggle"><input id="unpriced" v-model="state.showUnpriced" type="checkbox" /> Show unpriced eateries</label>
      </div>
    </header>
    <main>
      <aside>
        <p v-if="error" class="error">{{ error }}</p>
        <AboutPanel v-else-if="state.showAbout" />
        <VenueMenu v-else-if="state.panelOpen && state.selectedId" />
        <VenueList v-else />
      </aside>
      <LunchMap />
    </main>
  </div>
</template>
