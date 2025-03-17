<template>
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
          <p class="text-h5 font-weight-black">Fehler{{ feedbackStore.title ? ':' : '' }} {{ feedbackStore.title }}</p>
        </div>
        <div class="text-medium-emphasis">
          <p>
            {{ feedbackStore.message || 'Etwas ist schief gelaufen, bitte versuchen Sie es später erneut.' }}
          </p>
        </div>
      </v-card-text>
      <v-card-actions>
        <v-btn text @click="feedbackStore.clearFeedback()">Schließen</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

  <v-snackbar
    v-model="feedbackStore.show" 
    v-if="feedbackStore.type === 'snackbar'"
    transition="fade-transition"
    :timeout="3000"
    :color="feedbackStore.status === 'error' ? 'red' : 'success'" 
    variant="elevated"
    :key="feedbackStore.show ? 'snackbar-' + Date.now() : ''"
  >
    <h4 class="text-center align-center">
      <v-icon class="me-2"> 
        {{ feedbackStore.status === 'error' ? 'mdi-alert-circle-outline' : 'mdi-check-circle-outline' }}
      </v-icon>
      <template v-if="feedbackStore.title?.trim() && feedbackStore.status !== 'error'">
        {{ feedbackStore.title }}:
      </template>
      <template v-else-if="feedbackStore.status === 'error'">
        Fehler:
      </template>
      {{ feedbackStore.message || (feedbackStore.status === 'error' ? 'Etwas ist schief gelaufen, bitte versuchen Sie es später erneut.' : 'Die Aktion war erfolgreich.') }}
    </h4>
  </v-snackbar>
</template>

<script setup>
import { useFeedbackStore } from '@/stores/feedback';

const feedbackStore = useFeedbackStore();
</script>
