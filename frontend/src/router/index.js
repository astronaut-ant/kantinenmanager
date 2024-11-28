import { createRouter, createWebHistory } from "vue-router";
import index from "../pages/index.vue";
import Login from "../pages/Login.vue";
import { useAppStore } from "../stores/app.js";
import VerwaltungUebersicht from "@/pages/Verwaltung/VerwaltungUebersicht.vue";
import VerwaltungNeuerBenutzer from "../pages/Verwaltung/VerwaltungNeuerBenutzer.vue";
import VerwaltungBehinderung from "@/pages/Verwaltung/VerwaltungBehinderung.vue";
import KuecheUebersicht from "@/pages/Kuechenpersonal/KuecheUebersicht.vue";
import KuecheQR from "@/pages/Kuechenpersonal/KuecheQR.vue";
import AccessDenied from "@/pages/AccessDenied.vue";
import VerwaltungCsvUpload from "@/pages/Verwaltung/VerwaltungCsvUpload.vue";
import StandortUebersicht from "@/pages/Standortleitung/StandortleitungUebersicht.vue"
import StandortVertretung from "@/pages/Standortleitung/StandortleitungVertretung.vue"
import axios from "axios";

const routes = [
  { path: "/", component: index, redirect: "/login" },
  { path: "/login", component: Login },
  { path: "/accessdenied", component: AccessDenied },
  {
    path: "/verwaltung/uebersicht",
    component: VerwaltungUebersicht,
    beforeEnter: async (to, from, next) => {
      protectRoute(next, "verwaltung");
    },
  },
  {
    path: "/verwaltung/neuerBenutzer",
    component: VerwaltungNeuerBenutzer,
    beforeEnter: async (to, from, next) => {
      protectRoute(next, "verwaltung");
    },
  },
  {
    path: "/verwaltung/behinderung",
    component: VerwaltungBehinderung,
    beforeEnter: async (to, from, next) => {
      protectRoute(next, "verwaltung");
    },
  },
  {
    path: "/verwaltung/behinderung/csv-upload",
    component: VerwaltungCsvUpload,
    beforeEnter: async (to, from, next) => {
      protectRoute(next, "verwaltung");
    },
  },
  {
    path: "/kuechenpersonal/uebersicht",
    component: KuecheUebersicht,
    beforeEnter: async (to, from, next) => {
      protectRoute(next, "kuechenpersonal");
    },
  },

  {
    path: "/kuechenpersonal/qr",
    component: KuecheQR,
    beforeEnter: async (to, from, next) => {
      protectRoute(next, "kuechenpersonal");
    },
  },

  {
    path: "/standortleitung/uebersicht",
    component: StandortUebersicht,
    beforeEnter: async (to, from, next) => {
      protectRoute(next, "standortleitung");
    },
  },

  {
    path: "/standortleitung/vertretung",
    component: StandortVertretung,
    beforeEnter: async (to, from, next) => {
      protectRoute(next, "standortleitung");
    },
  },

];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

const protectRoute = (next, user_group) => {
  const appStore = useAppStore();
  try {
    if (appStore.userData.user_group == user_group) {
      next();
    } else next("/accessdenied");
  } catch (e) {
    next("/accessdenied");
  }
};

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
