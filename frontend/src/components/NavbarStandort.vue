<template>
  <nav>
    <v-toolbar class="bg-primary" flat app>
      <v-app-bar-nav-icon @click="showDrawer"></v-app-bar-nav-icon>
      <v-toolbar-title>
        <CustomBreadCrumbs
          :breadcrumbs="props.breadcrumbs"
          role="Standortleitung"
        />
      </v-toolbar-title>
      <Avatar />
    </v-toolbar>
    <v-navigation-drawer
      :disable-resize-watcher="true"
      class="elevation-10 bg-red"
      v-model="drawer"
      :width="230"
      app
    >
      <h1 class="mt-5 ms-4">Menu</h1>
      <hr class="text-white mt-4" />
      <div class="d-flex flex-column h-25 justify-space-evenly ms-4">
        <router-link
          to="/standortleitung/uebersicht"
          class="text-white text-decoration-none"
        >
          <v-icon class="me-1">mdi-account-group-outline</v-icon>
          Gruppenübersicht</router-link
        >

        <router-link
          to="/standortleitung/vertretung"
          class="text-white text-decoration-none"
        >
          <v-icon class="me-1">mdi-account-convert-outline</v-icon>
          Vertretung festlegen</router-link
        >
      </div>
    </v-navigation-drawer>
  </nav>
</template>

<script setup>
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
