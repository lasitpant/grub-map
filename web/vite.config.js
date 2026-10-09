import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

export default defineConfig({
  plugins: [vue()],
  base: "./",
  worker: { format: "es" }, // MapLibre's tile worker is an ES module
});
