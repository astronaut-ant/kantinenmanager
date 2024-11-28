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
        <router-link
          to="/verwaltung/uebersicht"
          class="text-white text-decoration-none"
        >
          <v-icon class="me-1">mdi-account-multiple</v-icon>
          Alle Benutzerkonten</router-link
        >

        <router-link
          to="/verwaltung/neuerBenutzer"
          class="text-white text-decoration-none"
        >
          <v-icon class="me-1">mdi-account-edit</v-icon>
          Neues Benutzerkonto</router-link
        >

        <router-link
          to="/verwaltung/behinderung"
          class="text-white text-decoration-none"
        >
          <v-icon class="me-1">mdi-wheelchair</v-icon>
          Mitarbeiter mit Behinderung</router-link
        >
      </div>
    </v-navigation-drawer>
  </nav>
</template>

<script setup>
import Avatar from "./Avatar.vue";

const drawer = ref(false);
const showDrawer = () => {
  drawer.value = !drawer.value;
};
</script>
