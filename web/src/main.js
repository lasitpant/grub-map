import { createApp } from "vue";
import "leaflet/dist/leaflet.css";
import "./styles.css";
import App from "./App.vue";
import { initAnalytics } from "./lib/analytics";

initAnalytics();
createApp(App).mount("#app");
