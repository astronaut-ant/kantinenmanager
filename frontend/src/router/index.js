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

const routes = [
  { path: "/", component: index, redirect: "/login" },
  { path: "/login", component: Login },
  { path: "/accessdenied", component: AccessDenied },
  {
    path: "/verwaltung/uebersicht",
    component: VerwaltungUebersicht,
    beforeEnter: (ton, from, next) => {
      protectRoute(next);
    },
  },
  {
    path: "/verwaltung/neuerBenutzer",
    component: VerwaltungNeuerBenutzer,
    beforeEnter: (ton, from, next) => {
      protectRoute(next);
    },
  },
  {
    path: "/verwaltung/behinderung",
    component: VerwaltungBehinderung,
    beforeEnter: (ton, from, next) => {
      protectRoute(next);
    },
  },
  {
    path: "/kuechenpersonal/uebersicht",
    component: KuecheUebersicht,
    beforeEnter: (ton, from, next) => {
      protectRoute(next);
    },
  },
  {
    path: "/kuechenpersonal/qr",
    component: KuecheQR,
    beforeEnter: (ton, from, next) => {
      protectRoute(next);
    },
  },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

const protectRoute = (next) => {
  const appStore = useAppStore();
  if (!appStore.auth) {
    next("/accessdenied");
  } else next();
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
