<template>
  <!-- Error Dialog -->
  <v-dialog 
    v-model="errorStore.show" v-if="errorStore.type === 'dialog'"
    no-click-animation
    persistent 
    max-width="400"
    >
    <v-card>
      <v-card-text>
        <div class="d-flex justify-center text-red mb-4">
          <p class="text-h5 font-weight-black">Fehler: {{ errorStore.title }}</p>
        </div>
        <div class="text-medium-emphasis">
          <p>
            {{ errorStore.message }}
          </p>
        </div>
      </v-card-text>
      <v-card-actions>
        <v-btn text @click="errorStore.clearError()">Schließen</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

  <!-- Error Snackbar -->
  <v-snackbar
    v-model="errorStore.show" v-if="errorStore.type === 'snackbar'"
    transition="fade-transition"
    :timeout="2500"
    color="red"
    variant="elevated"
  >
    <h4 class="text-center align-center">
      <v-icon class="me-2"> mdi-alert-circle-outline </v-icon> {{ errorStore.message }}
    </h4>
  </v-snackbar>
</template>


<script setup>
import { useErrorStore } from "@/stores/error";

const errorStore = useErrorStore();
</script>