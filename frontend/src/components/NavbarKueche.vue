<template>
  <nav>
    <v-toolbar class="bg-primary" flat app>
      <v-app-bar-nav-icon @click="showDrawer"></v-app-bar-nav-icon>
      <v-toolbar-title>
        <v-breadcrumbs density="comfortable" :items="[{ title: 'Küchenpersonal' }, ...breadcrumbs || []]">
          <template v-slot:prepend>
            <v-img src="@/assets/logo.png" />
          </template>
          <template v-slot:item="{ item }">
            <v-breadcrumbs-item>
              <span :style="`color: white;`">
                {{ item.title }}
              </span>
            </v-breadcrumbs-item>
          </template>
        </v-breadcrumbs>
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
          to="/kuechenpersonal/uebersicht"
          class="text-white text-decoration-none"
        >
          <v-icon class="me-1">mdi-list-box-outline</v-icon>
          Heutige Bestellungen</router-link
        >

        <router-link
          to="/kuechenpersonal/qr"
          class="text-white text-decoration-none"
        >
          <v-icon class="me-1">mdi-qrcode-scan</v-icon>
          QR-Scanner</router-link
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
    required: false
  }
});
</script>
