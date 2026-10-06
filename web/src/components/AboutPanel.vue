<script setup>
import { state } from "../lib/store";

const REPO = "https://github.com/lasitpant/grub-map";
</script>

<template>
  <article class="detail about">
    <button type="button" class="back" @click="state.showAbout = false">← All spots</button>
    <h2>About Grub Map</h2>
    <p class="lead">
      Grub Map finds real lunch deals in Dublin city centre for under €10 and €12, with the dish, the price
      and where that price came from.
    </p>

    <h3>Why it exists</h3>
    <p>
      Lunch in Dublin adds up fast. A sandwich and a coffee can easily cost €15, which is a lot for students and for
      people early in their careers working in the city. Good cheap lunches do exist, but they're scattered across
      old articles, Reddit threads and word of mouth. Grub Map puts them on one map, so you can see what's
      near you and what it costs before you walk out the door.
    </p>

    <h3>No money from restaurants</h3>
    <ul class="promise">
      <li>Restaurants can't pay to be listed, featured or ranked higher. Ever.</li>
      <li>Grub Map gets no money, commission or free food from any restaurant on the map.</li>
      <li>Spots are sorted by price only. Nobody gets a better position.</li>
      <li>It's a non-commercial side project. Hosting is paid out of pocket.</li>
    </ul>

    <h3>Where the prices come from</h3>
    <p>
      Each price shows its source and the date it was collected: a published guide, the venue's own menu, or a visit.
      Prices change, so please check before you go. If you've just eaten somewhere, tap
      <b>👍 Still €…</b> or <b>Price changed</b> on the deal. That one tap keeps the map honest for everyone.
    </p>
    <p>Locations, opening hours and websites come from OpenStreetMap, made by volunteers.</p>

    <h3>Your privacy</h3>
    <p>
      No accounts, no cookies, no personal data. Visits and clicks are counted anonymously with GoatCounter, and
      price votes store only the deal, the vote and the time.
    </p>

    <h3>Get involved</h3>
    <p>
      Know a great lunch under €12 that's missing, or spotted a mistake? Grub Map is open source:
      <a :href="REPO" target="_blank" rel="noopener">see the code or suggest a deal on GitHub</a>.
    </p>
  </article>
</template>
