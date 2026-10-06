<script setup>
// "Still €9?" one-tap check on a lunch deal. Anonymous: nothing about the person is sent or stored.
// Hidden entirely when no backend is configured (VITE_API_BASE unset).
import { computed, ref } from "vue";
import { API, sendFeedback } from "../lib/api";
import { state, euro, ago } from "../lib/store";
import { track } from "../lib/analytics";

const props = defineProps({ deal: Object, venue: Object });

// One vote per deal per day from this browser, kept on the device only.
const VOTES_KEY = "grub-map:votes";
const today = () => new Date().toISOString().slice(0, 10);
function votedToday(id) {
  try { return JSON.parse(localStorage.getItem(VOTES_KEY) || "{}")[id] === today(); } catch { return false; }
}
function rememberVote(id) {
  try {
    const all = JSON.parse(localStorage.getItem(VOTES_KEY) || "{}");
    for (const k of Object.keys(all)) if (all[k] !== today()) delete all[k];
    localStorage.setItem(VOTES_KEY, JSON.stringify({ ...all, [id]: today() }));
  } catch {}
}

const stats = computed(() => state.feedback[props.deal.id] ?? { still: 0, changed: 0 });
// Show a warning only when recent "changed" reports outnumber recent confirmations.
const disputed = computed(() => stats.value.changed > 0 && stats.value.changed >= stats.value.still);

const mode = ref(votedToday(props.deal.id) ? "done" : "ask"); // ask | price | sending | done
const newPrice = ref("");
const error = ref("");

async function vote(kind) {
  error.value = "";
  const price = kind === "changed" && newPrice.value !== "" ? Number(newPrice.value) : undefined;
  if (price !== undefined && !(price > 0 && price <= 100)) {
    error.value = "Enter the new price in euro, e.g. 9.50, or leave it blank.";
    return;
  }
  mode.value = "sending";
  try {
    await sendFeedback(props.deal.id, kind, price);
    rememberVote(props.deal.id);
    const s = { ...stats.value };
    s[kind] += 1;
    s[`last_${kind}`] = new Date().toISOString();
    state.feedback = { ...state.feedback, [props.deal.id]: s };
    track(`price-${kind}/${props.venue.brand}`, `${props.venue.name} · ${kind === "still" ? "still this price" : "price changed"}`);
    mode.value = "done";
  } catch (e) {
    error.value = e.message;
    mode.value = kind === "changed" ? "price" : "ask";
  }
}
</script>

<template>
  <div v-if="API" class="feedback">
    <p v-if="disputed" class="meta warn">
      {{ stats.changed }} {{ stats.changed === 1 ? "person" : "people" }} reported a different price
      {{ ago(stats.last_changed) }}. Check before you go.
    </p>
    <p v-else-if="stats.still" class="meta">
      ✓ Confirmed by {{ stats.still }} {{ stats.still === 1 ? "person" : "people" }}, last {{ ago(stats.last_still) }}
    </p>

    <div v-if="mode === 'ask'" class="fb-buttons">
      <button type="button" class="fb" @click="vote('still')">👍 Still {{ euro(deal.price) }}</button>
      <button type="button" class="fb fb-quiet" @click="mode = 'price'">Price changed</button>
    </div>

    <form v-else-if="mode === 'price' || mode === 'sending'" class="fb-buttons" @submit.prevent="vote('changed')">
      <label class="meta" :for="`np-${deal.id}`">New price €</label>
      <input :id="`np-${deal.id}`" v-model="newPrice" class="fb-input" type="number" inputmode="decimal"
             min="0.5" max="100" step="0.01" placeholder="optional" />
      <button type="submit" class="fb" :disabled="mode === 'sending'">Send</button>
      <button type="button" class="fb fb-quiet" :disabled="mode === 'sending'" @click="mode = 'ask'">Cancel</button>
    </form>

    <p v-else-if="mode === 'done'" class="meta" role="status">Thanks! That keeps prices honest for everyone.</p>
    <p v-if="error" class="meta warn" role="alert">{{ error }}</p>
  </div>
</template>
