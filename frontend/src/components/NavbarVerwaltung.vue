<template>
  <nav>
    <v-toolbar class="bg-primary" flat app>
      <v-app-bar-nav-icon @click="showDrawer"></v-app-bar-nav-icon>
      <v-toolbar-title>
        <CustomBreadCrumbs :breadcrumbs="props.breadcrumbs" role="Verwaltung" />
      </v-toolbar-title>
      <Avatar />
    </v-toolbar>
    <v-navigation-drawer
      :disable-resize-watcher="true"
      class="elevation-10 bg-red"
      :width="230"
      v-model="drawer"
      app
    >
      <h1 class="mt-5 ms-4">Menu</h1>
      <hr class="text-white mt-4" />
      <div class="d-flex flex-column h-50 justify-space-evenly">
        <Dropdown
          menuName="Benutzer"
          menuIcon="mdi-account"
          :items="[
            {
              title: 'Alle Benutzer',
              icon: 'mdi-format-list-bulleted',
              link: '/verwaltung/benutzer/uebersicht',
            },
            {
              title: 'Neuer Benutzer',
              icon: 'mdi-plus',
              link: '/verwaltung/benutzer/neuerBenutzer',
            },
          ]"
        />

        <Dropdown
          menuName="Standorte"
          menuIcon="mdi-home-group"
          :items="[
            {
              title: 'Alle Standorte',
              icon: 'mdi-format-list-bulleted',
              link: '/verwaltung/standorte/uebersicht',
            },
            {
              title: 'Neuer Standort',
              icon: 'mdi-plus',
              link: '/verwaltung/standorte/neuerStandort',
            },
          ]"
        />

        <Dropdown
          menuName="Gruppen"
          menuIcon="mdi-account-group"
          :items="[
            {
              title: 'Alle Gruppen',
              icon: 'mdi-format-list-bulleted',
              link: '/verwaltung/gruppen/uebersicht',
            },
            {
              title: 'Neue Gruppe',
              icon: 'mdi-plus',
              link: '/verwaltung/gruppen/neueGruppe',
            },
          ]"
        />

        <Dropdown
          menuName="Mitarbeiter"
          menuIcon="mdi-wheelchair"
          :items="[
            {
              title: 'Alle Mitarbeiter',
              icon: 'mdi-format-list-bulleted',
              link: '/verwaltung/mitarbeiter/uebersicht',
            },
            {
              title: 'Neuer Mitarbeiter',
              icon: 'mdi-plus',
              link: '/verwaltung/mitarbeiter/neuerMitarbeiter',
            },
          ]"
        />

        <Dropdown
          menuName="Abrechnung"
          menuIcon="mdi-invoice-edit-outline"
          :items="[
            {
              title: 'Abrechnung erstellen',
              icon: 'mdi-plus',
              link: '/verwaltung/abrechnung/neueAbrechnung',
            },
            {
              title: 'Preise Anpassen',
              icon: 'mdi-calculator',
              link: '/verwaltung/abrechnung/essensPreise',
            },
          ]"
        />
      </div>
    </v-navigation-drawer>
  </nav>
</template>

<script setup>
import Avatar from "./Avatar.vue";
import CustomBreadCrumbs from "./CustomBreadCrumbs.vue";
import Dropdown from "./Dropdown.vue";

const drawer = ref(false);
const showDrawer = () => {
  drawer.value = !drawer.value;
};

const props = defineProps({
  breadcrumbs: {
    type: Array,
    required: false,
  },
});
</script>
