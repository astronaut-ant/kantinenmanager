import { createRouter, createWebHistory } from "vue-router";
import index from "../pages/index.vue";
import Login from "../pages/login.vue";
import { useAppStore } from "../stores/app.js";
import VerwaltungAlleBenutzer from "@/pages/Verwaltung/VerwaltungAlleBenutzer.vue";
import VerwaltungNeuerBenutzer from "../pages/Verwaltung/VerwaltungNeuerBenutzer.vue";
import VerwaltungNeuerMitarbeiter from "@/pages/Verwaltung/VerwaltungNeuerMitarbeiter.vue";
import KuecheUebersicht from "@/pages/Kuechenpersonal/KuecheUebersicht.vue";
import KuecheQR from "@/pages/Kuechenpersonal/KuecheQR.vue";
import AccessDenied from "@/pages/AccessDenied.vue";
import VerwaltungNeuerMitarbeiterCsvUpload from "@/pages/Verwaltung/VerwaltungNeuerMitarbeiterCsvUpload.vue";
import StandortUebersicht from "@/pages/Standortleitung/StandortleitungUebersicht.vue";
import StandortVertretung from "@/pages/Standortleitung/StandortleitungVertretung.vue";
import axios from "axios";
import VerwaltungAlleMitarbeiter from "@/pages/Verwaltung/VerwaltungAlleMitarbeiter.vue";
import VerwaltungAlleStandorte from "@/pages/Verwaltung/VerwaltungAlleStandorte.vue";
import VerwaltungNeuerStandort from "@/pages/Verwaltung/VerwaltungNeuerStandort.vue";
import VerwaltungAlleGruppen from "@/pages/Verwaltung/VerwaltungAlleGruppen.vue";
import VerwaltungNeueGruppe from "@/pages/Verwaltung/VerwaltungNeueGruppe.vue";
import VerwaltungMitarbeiterManuell from "@/pages/Verwaltung/VerwaltungMitarbeiterManuell.vue";
import GruppenleitungVorbestellungen from "@/pages/Gruppenleitung/GruppenleitungVorbestellungen.vue";
import GruppenleitungMeineGruppen from "@/pages/Gruppenleitung/GruppenleitungMeineGruppen.vue";
import Impressum from "@/pages/Impressum.vue";
import Datenschutzerklaerung from "@/pages/Datenschutzerklaerung.vue";

const routes = [
  { path: "/", component: index, redirect: "/login" },
  { path: "/impressum", component: Impressum },
  { path: "/datenschutzerklaerung", component: Datenschutzerklaerung },
  { path: "/accessdenied", component: AccessDenied },
  {
    path: "/login",
    component: Login,
    beforeEnter: (to, from, next) => {
      let user_group = "";
      axios
        .get(import.meta.env.VITE_API + "/api/is-logged-in", {
          withCredentials: true,
        })
        .then((response) => {
          user_group = response.data.user_group;
          if (user_group === "verwaltung") {
            next("/verwaltung/benutzer/uebersicht");
          }
          if (user_group === "gruppenleitung") {
            next("/gruppenleitung/meineGruppen");
          }
          if (user_group === "standortleitung") {
            next("/standortleitung/uebersicht");
          }
          if (user_group === "kuechenpersonal") {
            next("/kuechenpersonal/uebersicht");
          }
        })
        .catch((err) => next());
    },
  },
  {
    path: "/verwaltung/benutzer/uebersicht",
    component: VerwaltungAlleBenutzer,
    beforeEnter: (to, from, next) => {
      protectRoute(next, "verwaltung");
    },
  },
  {
    path: "/verwaltung/benutzer/neuerBenutzer",
    component: VerwaltungNeuerBenutzer,
    beforeEnter: (to, from, next) => {
      protectRoute(next, "verwaltung");
    },
  },
  {
    path: "/verwaltung/mitarbeiter/uebersicht",
    component: VerwaltungAlleMitarbeiter,
    beforeEnter: (to, from, next) => {
      protectRoute(next, "verwaltung");
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
    path: "/kuechenpersonal/uebersicht",
    component: KuecheUebersicht,
    beforeEnter: (to, from, next) => {
      protectRoute(next, "kuechenpersonal");
    },
  },

  {
    path: "/kuechenpersonal/qr",
    component: KuecheQR,
    beforeEnter: (to, from, next) => {
      protectRoute(next, "kuechenpersonal");
    },
  },

  {
    path: "/standortleitung/uebersicht",
    component: StandortUebersicht,
    beforeEnter: (to, from, next) => {
      protectRoute(next, "standortleitung");
    },
  },

  {
    path: "/standortleitung/vertretung",
    component: StandortVertretung,
    beforeEnter: (to, from, next) => {
      protectRoute(next, "standortleitung");
    },
  },
  {
    path: "/gruppenleitung/meineGruppen",
    component: GruppenleitungMeineGruppen,
    beforeEnter: (to, from, next) => {
      protectRoute(next, "gruppenleitung");
    },
  },
  {
    path: "/gruppenleitung/vorbestellungen",
    component: GruppenleitungVorbestellungen,
    beforeEnter: (to, from, next) => {
      protectRoute(next, "gruppenleitung");
    },
  },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

const protectRoute = (next, user_group) => {
  axios
    .get(import.meta.env.VITE_API + "/api/is-logged-in", {
      withCredentials: true,
    })
    .then((response) => {
      console.log(response.data);
      if (response.data.user_group === user_group) {
        next();
      } else {
        next("/accessdenied");
      }
    })
    .catch((err) => next("/accessdenied"));
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
