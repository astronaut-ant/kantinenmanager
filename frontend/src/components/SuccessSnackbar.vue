<template>
    <v-snackbar
      v-model="localsnackbar"
      :timeout="10000"
      color="success"
      variant="outlined"
    >
    <v-icon left class="mr-2"> mdi-check-circle-outline </v-icon> {{ text }}
      <template v-slot:actions>
        <v-btn
          color="success"
          variant="text"
          @click="closesnackbar"
        >
          Schliessen
        </v-btn>
      </template>
    </v-snackbar>
  </template>
  
  <script setup>
  const props = defineProps(["text"]);
  const emit = defineEmits(["close"]);


  const closesnackbar = () => {
    emit("close");
  };
  </script>
  


