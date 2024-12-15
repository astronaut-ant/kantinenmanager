<template>
  <v-snackbar
    v-model="localsnackbar"
    transition="fade-transition"
    :timeout="2500"
    color="success"
    variant="elevated"
  >
    <v-icon left class="mr-2"> mdi-check-circle-outline </v-icon> {{ text }}
    <template v-slot:actions>
      <!-- <v-btn color="success" variant="text" @click="closesnackbar">
        Schliessen
      </v-btn> -->
    </template>
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
