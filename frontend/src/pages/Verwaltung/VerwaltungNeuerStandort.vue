<template>
  <NavbarVerwaltung :breadcrumbs = '[{"title": "Standorte"}, {"title": "Neuer Standort"}]'/>
  <LocationCreation :key="forcer" @close="reset" />
  <SuccessSnackbar
    v-model="snackbar"
    text="Standort erfolgreich angelegt!"
    @close="snackbar = false"
  ></SuccessSnackbar>
</template>
<script setup>
import LocationCreation from "@/components/LocationCreation.vue";
const forcer = ref(1);
const snackbar = ref(false);
const reset = () => {
  forcer.value += 1;
  forcer.value %= 2;
  snackbar.value = true;
};
</script>
