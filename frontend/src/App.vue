<template>
  <v-app>
    <v-main class="main-content">
      <router-view />
    </v-main>
    <Footer v-if="useRoute().path !== '/accessdenied'"></Footer>
    <GlobalFeedback />
  </v-app>
</template>

<script setup>
import { useRoute } from 'vue-router';
import Footer from './components/Footer.vue';
import GlobalFeedback from './components/GlobalFeedback.vue';
</script>

<style>
.main-content {
  min-height: calc(100vh - 92px);
}
</style>