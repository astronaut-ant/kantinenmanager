<template>
  <!-- Error Banner -->
  <v-banner 
    v-if="errorStore.show && errorStore.type === 'banner'" 
    color="error" 
    icon="mdi-alert"
    >
    {{ errorStore.message }}
  </v-banner>

  <!-- Error Dialog -->
  <v-dialog 
    v-model="errorStore.show" v-if="errorStore.type === 'dialog'" 
    max-width="400"
    >
    <v-card>
      <v-card-title>
        Error
      </v-card-title>
      <v-card-text>
        {{ errorStore.message }}
      </v-card-text>
      <v-card-actions>
        <v-btn 
            @click="errorStore.clearError()"
            >
            Close
        </v-btn>
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