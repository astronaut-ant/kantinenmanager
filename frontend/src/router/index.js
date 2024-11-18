import { createRouter, createWebHistory } from "vue-router";
import gruppenleitung from "../pages/gruppenleitung.vue";
import index from "../pages/index.vue";
import kuechenpersonal from "../pages/kuechenpersonal.vue";
import verwaltung from "../pages/verwaltung_neuerBenutzer.vue";
import standortleitung from "../pages/standortleitung.vue";
import login from "../pages/login.vue";
import { useAppStore } from "../stores/app.js";
import Verwaltung_Uebersicht from "@/pages/verwaltung_Uebersicht.vue";
import Verwaltung_neuerBenutzer from "../pages/verwaltung_neuerBenutzer.vue";
import Verwaltung_behinderung from "@/pages/verwaltung_behinderung.vue";

const routes = [
  { path: "/", component: index, redirect: "/login" },
  {
    path: "/gruppenleitung",
    component: gruppenleitung,
    // beforeEnter: (to, from, next) => {
    //   const appStore = useAppStore();
    //   if (!appStore.auth) {
    //     next("/login");
    //   } else next();
    // },
  },
  {
    path: "/standortleitung",
    component: standortleitung,
    // beforeEnter: (to, from, next) => {
    //   const appStore = useAppStore();
    //   if (!appStore.auth) {
    //     next("/login");
    //   } else next();
    // },
  },
  {
    path: "/verwaltung/uebersicht",
    component: Verwaltung_Uebersicht,
    // beforeEnter: (to, from, next) => {
    //   const appStore = useAppStore();
    //   if (!appStore.auth) {
    //     next("/login");
    //   } else next();
    // },
  },

  {
    path: "/verwaltung/neuerBenutzer",
    component: Verwaltung_neuerBenutzer,
    // beforeEnter: (to, from, next) => {
    //   const appStore = useAppStore();
    //   if (!appStore.auth) {
    //     next("/login");
    //   } else next();
    // },
  },
  {
    path: "/verwaltung/behinderung",
    component: Verwaltung_behinderung,
    // beforeEnter: (to, from, next) => {
    //   const appStore = useAppStore();
    //   if (!appStore.auth) {
    //     next("/login");
    //   } else next();
    // },
  },
  {
    path: "/kuechenpersonal",
    component: kuechenpersonal,
    // beforeEnter: (to, from, next) => {
    //   const appStore = useAppStore();
    //   if (!appStore.auth) {
    //     next("/login");
    //   } else next();
    // },
  },

  { path: "/login", component: login },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

// Workaround for https://github.com/vitejs/vite/issues/11804
router.onError((err, to) => {
  if (err?.message?.includes?.("Failed to fetch dynamically imported module")) {
    if (!localStorage.getItem("vuetify:dynamic-reload")) {
      console.log("Reloading page to fix dynamic import error");
      localStorage.setItem("vuetify:dynamic-reload", "true");
      location.assign(to.fullPath);
    } else {
      console.error("Dynamic import error, reloading page did not fix it", err);
    }
  } else {
    console.error(err);
  }
});

router.isReady().then(() => {
  localStorage.removeItem("vuetify:dynamic-reload");
});

export default router;
