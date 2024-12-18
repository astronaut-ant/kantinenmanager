<template>
  <v-snackbar
    v-model="localsnackbar"
    transition="fade-transition"
    :timeout="2500"
    color="success"
    variant="elevated"
  >
    <h4 class="text-center align-center">
      <v-icon class="me-2"> mdi-check-circle-outline </v-icon> {{ text }}
    </h4>
  </v-snackbar>
</template>

<script setup>
const localsnackbar = ref(false);
const props = defineProps(["text"]);
// const emit = defineEmits(["close"]);

// const closesnackbar = () => {
//   emit("close");
// };
</script>
