<template>
  <h1 class="text-center mt-5 text-pink">Frontend ... under construction</h1>
  <div class="d-flex justify-center mt-5 ga-5">
    <v-btn class="text-dark" to="../testroute">testRoute#</v-btn>
    <v-btn class="bg-pink">Backend check</v-btn>
  </div>
  <div v-if="showConfirm" class="d-flex justify-center">
    <h3></h3>
    <v-icon
      class="mt-6"
      color="success"
      icon="mdi-check-circle-outline"
      size="128"
    >
    </v-icon>
  </div>
</template>

<script setup>
const showConfirm = ref(false);
</script>
