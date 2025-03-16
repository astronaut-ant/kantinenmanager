<template>
  <NavbarVerwaltung :breadcrumbs = '[{"title": "Standorte"}, {"title": "Neuer Standort"}]'/>
  <LocationCreation :key="forcer" @close="reset">
    <template v-slot:confirm>
      <div
        v-if="showConfirm"
        class="mt-5 d-flex justify-center align-center ga-5"
      >
        <h3>Hinzugefügt!</h3>
        <v-icon color="success" icon="mdi-check-circle-outline" size="32">
        </v-icon>
      </div>
    </template>
  </LocationCreation>
</template>
<script setup>
import { useFeedbackStore } from "@/stores/feedback";
const feedbackStore = useFeedbackStore();
import LocationCreation from "@/components/LocationCreation.vue";
const forcer = ref(1);
const showConfirm = ref(false);
const reset = () => {
  forcer.value += 1;
  forcer.value %= 2;
  showConfirm.value = true;
  setTimeout(() => {
    showConfirm.value = false;
  }, 1500);
};
</script>
