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
import VerwaltungNeuerMitarbeiterCsvUpload from "@/pages/Verwaltung/VerwaltungNeuerMitarbeiterCsvUpload.vue";
import axios from "axios";
import Gruppenleitung from "@/pages/Gruppenleitung/Gruppenleitung.vue";
import Standortleitung from "@/pages/Standortleitung/Standortleitung.vue";
import VerwaltungAlleMitarbeiter from "@/pages/Verwaltung/VerwaltungAlleMitarbeiter.vue";
import VerwaltungAlleStandorte from "@/pages/Verwaltung/VerwaltungAlleStandorte.vue";
import VerwaltungNeuerStandort from "@/pages/Verwaltung/VerwaltungNeuerStandort.vue";
import VerwaltungAlleGruppen from "@/pages/Verwaltung/VerwaltungAlleGruppen.vue";
import VerwaltungNeueGruppe from "@/pages/Verwaltung/VerwaltungNeueGruppe.vue";
import VerwaltungMitarbeiterManuell from "@/pages/Verwaltung/VerwaltungMitarbeiterManuell.vue";

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
    path: "/verwaltung/mitarbeiter/neuerMitarbeiter",
    component: VerwaltungNeuerMitarbeiter,
    beforeEnter: (to, from, next) => {
      protectRoute(next, "verwaltung");
    },
  },
  {
    path: "/verwaltung/mitarbeiter/neuerMitarbeiterCsvUpload",
    component: VerwaltungNeuerMitarbeiterCsvUpload,
    beforeEnter: (to, from, next) => {
      protectRoute(next, "verwaltung");
    },
  },
  {
    path: "/verwaltung/mitarbeiter/neuerMitarbeiterManuell",
    component: VerwaltungMitarbeiterManuell,
    beforeEnter: (to, from, next) => {
      protectRoute(next, "verwaltung");
    },
  },
  {
    path: "/verwaltung/standorte/uebersicht",
    component: VerwaltungAlleStandorte,
    beforeEnter: (to, from, next) => {
      protectRoute(next, "verwaltung");
    },
  },
  {
    path: "/verwaltung/standorte/neuerStandort",
    component: VerwaltungNeuerStandort,
    beforeEnter: (to, from, next) => {
      protectRoute(next, "verwaltung");
    },
  },

  {
    path: "/verwaltung/gruppen/uebersicht",
    component: VerwaltungAlleGruppen,
    beforeEnter: (to, from, next) => {
      protectRoute(next, "verwaltung");
    },
  },

  {
    path: "/verwaltung/gruppen/neueGruppe",
    component: VerwaltungNeueGruppe,
    beforeEnter: (to, from, next) => {
      protectRoute(next, "verwaltung");
    },
  },

  {
    path: "/gruppenleitung/uebersicht",
    component: Gruppenleitung,
    beforeEnter: (to, from, next) => {
      protectRoute(next, "gruppenleitung");
    },
  },
  {
    path: "/standortleitung/uebersicht",
    component: Standortleitung,
    beforeEnter: (to, from, next) => {
      protectRoute(next, "standortleitung");
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
  next();
  // const appStore = useAppStore();
  // if (!appStore.auth) {
  //   next("/accessdenied");
  // } else next();
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
