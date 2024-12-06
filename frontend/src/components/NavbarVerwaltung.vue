<template>
  <nav>
    <v-toolbar class="bg-primary" flat app>
      <v-app-bar-nav-icon @click="showDrawer"></v-app-bar-nav-icon>
      <v-toolbar-title>
        <span>Verwaltung</span>
      </v-toolbar-title>
      <Avatar />
    </v-toolbar>
    <v-navigation-drawer
      :disable-resize-watcher="true"
      class="elevation-10 bg-red"
      v-model="drawer"
      app
    >
      <h1 class="mt-5 ps-2">Menu</h1>
      <hr class="text-white mt-4" />
      <div class="d-flex flex-column h-75 justify-space-evenly ps-2">
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
              icon: 'mdi-pencil-plus-outline',
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
              icon: 'mdi-pencil-plus-outline',
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
              icon: 'mdi-pencil-plus-outline',
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
              icon: 'mdi-pencil-plus-outline',
              link: '/verwaltung/mitarbeiter/neuerMitarbeiter',
            },
          ]"
        />
      </div>
    </v-navigation-drawer>
  </nav>
</template>

<script setup>
import Avatar from "./Avatar.vue";
import Dropdown from "./Dropdown.vue";

const drawer = ref(false);
const showDrawer = () => {
  drawer.value = !drawer.value;
};
</script>
