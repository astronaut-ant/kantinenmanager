import { createRouter, createWebHistory } from "vue-router";
import gruppenleitung from "../pages/Gruppenleitung/Gruppenleitung.vue";
import index from "../pages/index.vue";
import kuechenpersonal from "../pages/Kuechenpersonal/Kuechenpersonal.vue";
import verwaltung from "../pages/Verwaltung/VerwaltungNeuerBenutzer.vue";
import VerwaltungCSVUpload from "@/pages/Verwaltung/VerwaltungCsvUpload.vue";
import standortleitung from "../pages/Standortleitung/Standortleitung.vue";
import login from "../pages/Login.vue";
import { useAppStore } from "../stores/app.js";
import VerwaltungUebersicht from "@/pages/Verwaltung/VerwaltungUebersicht.vue";
import VerwaltungNeuerBenutzer from "../pages/Verwaltung/VerwaltungNeuerBenutzer.vue";
import VerwaltungBehinderung from "@/pages/Verwaltung/VerwaltungBehinderung.vue";

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
    component: VerwaltungUebersicht,
    // beforeEnter: (to, from, next) => {
    //   const appStore = useAppStore();
    //   if (!appStore.auth) {
    //     next("/login");
    //   } else next();
    // },
  },

  {
    path: "/verwaltung/neuerBenutzer",
    component: VerwaltungNeuerBenutzer,
    // beforeEnter: (to, from, next) => {
    //   const appStore = useAppStore();
    //   if (!appStore.auth) {
    //     next("/login");
    //   } else next();
    // },
  },
  {
    path: "/verwaltung/behinderung",
    component: VerwaltungBehinderung,
    // beforeEnter: (to, from, next) => {
    //   const appStore = useAppStore();
    //   if (!appStore.auth) {
    //     next("/login");
    //   } else next();
    // },
  },

  {
    path: "/verwaltung/behinderung/csv-upload",
    component: VerwaltungCSVUpload,
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
