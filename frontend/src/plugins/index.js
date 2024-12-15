/**
 * plugins/index.js
 *
 * Automatically included in `./src/main.js`
 */

// Plugins
import vuetify from "./vuetify";
import pinia from "@/stores";
import router from "@/router";
import piniaPluginPersistedState from "pinia-plugin-persistedstate";

export function registerPlugins(app) {
  app.use(vuetify).use(router).use(pinia);
  pinia.use(piniaPluginPersistedState);
}
