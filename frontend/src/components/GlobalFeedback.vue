<template>
  <!-- Error Dialog -->
  <v-dialog 
    v-model="feedbackStore.show" 
    v-if="feedbackStore.type === 'dialog' && feedbackStore.status === 'error'"
    no-click-animation
    persistent 
    max-width="500"
    >
    <v-card>
      <v-card-text>
        <div class="d-flex justify-center text-red mb-4">
          <p class="text-h5 font-weight-black">Fehler{{ feedbackStore.title === "" ? '' : ':' }} {{ feedbackStore.title }}</p>
        </div>
        <div class="text-medium-emphasis">
          <p>
            {{ feedbackStore.message }}
          </p>
        </div>
      </v-card-text>
      <v-card-actions>
        <v-btn text @click="feedbackStore.clearFeedback()">Schließen</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

  <!-- Error Snackbar -->
  <v-snackbar
    v-model="feedbackStore.show" 
    v-if="feedbackStore.type === 'snackbar'"
    transition="fade-transition"
    :timeout="2500"
    :color="feedbackStore.status === 'error' ? 'red' : 'success'" 
    variant="elevated"
    :key="feedbackStore.show ? 'snackbar-' + Date.now() : ''"
  >
    <h4 class="text-center align-center">
      <v-icon class="me-2"> {{ feedbackStore.status === 'error' ? 'mdi-alert-circle-outline' : 'mdi-check-circle-outline' }} </v-icon>
      {{ feedbackStore.title }}{{ feedbackStore.title === "" ? '' : ':' }} {{ feedbackStore.message }}
    </h4>
  </v-snackbar>
</template>


<script setup>
import { useFeedbackStore } from '@/stores/feedback';

const feedbackStore = useFeedbackStore();
</script>