<template>
  <NavbarVerwaltung :breadcrumbs = '[{"title": "Standorte"}, {"title": "Neuer Standort"}]'/>
  <LocationCreation :key="forcer" @close="reset" />
</template>
<script setup>
import { useFeedbackStore } from "@/stores/feedback";
const feedbackStore = useFeedbackStore();
import LocationCreation from "@/components/LocationCreation.vue";
const forcer = ref(1);
const reset = () => {
  forcer.value += 1;
  forcer.value %= 2;
  feedbackStore.setFeedback("success", "snackbar", "", "Standort wurde erfolgreich angelegt!");
};
</script>
