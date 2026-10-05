<script setup>
import { onMounted, ref } from "vue";
import { getVenues, getMenus } from "./lib/api";
import { state, categories } from "./lib/store";
import LunchMap from "./components/LunchMap.vue";
import VenueList from "./components/VenueList.vue";
import VenueMenu from "./components/VenueMenu.vue";

const error = ref("");
onMounted(async () => {
  try {
    [state.venues, state.menus] = await Promise.all([getVenues(), getMenus()]);
  } catch (e) {
    error.value = `${e.message}. Run pipeline/export.py, then reload.`;
  }
});
</script>

<template>
  <div class="app">
    <header>
      <h1>Grub Map <small>Dublin lunches under €10 and €12</small></h1>
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
        <label class="toggle"><input id="unpriced" v-model="state.showUnpriced" type="checkbox" /> Show unpriced eateries</label>
      </div>
    </header>
    <main>
      <aside>
        <p v-if="error" class="error">{{ error }}</p>
        <VenueMenu v-else-if="state.selectedId" />
        <VenueList v-else />
      </aside>
      <LunchMap />
    </main>
  </div>
</template>
