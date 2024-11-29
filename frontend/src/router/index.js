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
import axios from "axios";
import Gruppenleitung from "@/pages/Gruppenleitung/Gruppenleitung.vue";
import Standortleitung from "@/pages/Standortleitung/Standortleitung.vue";

const routes = [
  { path: "/", component: index, redirect: "/login" },
  { path: "/accessdenied", component: AccessDenied },
  {
    path: "/login",
    component: Login,
    beforeEnter: (to, from, next) => {
      let user_group = "";
      axios
        .get("http://localhost:4200/api/is-logged-in", {
          withCredentials: true,
        })
        .then((response) => {
          user_group = response.data.user_group;
          next(`/${user_group}/uebersicht`);
        })
        .catch((err) => next());
    },
  },
  {
    path: "/verwaltung/uebersicht",
    component: VerwaltungUebersicht,
    beforeEnter: (to, from, next) => {
      protectRoute(next, "verwaltung");
    },
  },
  {
    path: "/verwaltung/neuerBenutzer",
    component: VerwaltungNeuerBenutzer,
    beforeEnter: (to, from, next) => {
      protectRoute(next, "verwaltung");
    },
  },
  {
    path: "/verwaltung/behinderung",
    component: VerwaltungBehinderung,
    beforeEnter: (to, from, next) => {
      protectRoute(next, "verwaltung");
    },
  },
  {
    path: "/verwaltung/behinderung/csv-upload",
    component: VerwaltungCsvUpload,
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
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

const protectRoute = (next, user_group) => {
  axios
    .get("http://localhost:4200/api/is-logged-in", { withCredentials: true })
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
