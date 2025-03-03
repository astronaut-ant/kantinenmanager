<template>
  <v-app>
    <v-main class="main-content">
      <router-view />
    </v-main>
    <Footer></Footer>
  </v-app>
</template>

<script setup>
//
</script>

<style>
.main-content {
  min-height: calc(100vh - 64px);
}
</style>