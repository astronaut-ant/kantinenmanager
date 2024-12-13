<template>
  <v-snackbar
    transition="fade-transition"
    :model-value="props.showSnackbar"
    :timeout="-1"
    color="success"
  >
    <div class="d-flex h-100 align-center">
      <AnimatedCircle class="w-25" />
      <h4 class="text-white">Passwort erfolgreich geändert</h4>
    </div>
  </v-snackbar>
</template>

<script setup>
const props = defineProps(["showSnackbar"]);
</script>
