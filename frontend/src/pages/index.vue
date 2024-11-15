<template>
  <h1 class="text-center mt-5 text-pink">Frontend ... under construction!!!</h1>
  <div class="d-flex justify-center mt-5 ga-5">
    <v-btn class="text-dark" to="../verwaltung">Verwaltung</v-btn>
    <v-btn class="text-dark" to="../standortleitung">Standortleitung</v-btn>
    <v-btn class="text-dark" to="../gruppenleitung">Gruppenleitung</v-btn>
    <v-btn class="text-dark" to="../kuechenpersonal">Küchenpersonal</v-btn>
    <v-btn class="text-dark" to="../login">login</v-btn>
    <v-btn @click="testBackend" class="bg-pink">Backend check</v-btn>
  </div>
  <div v-if="showConfirm" class="mt-5 d-flex justify-center align-center ga-5">
    <h3>{{ backEndAnswer.health_status }}</h3>
    <v-icon color="success" icon="mdi-check-circle-outline" size="32"> </v-icon>
  </div>
</template>

<script setup>
const showConfirm = ref(false);
const backEndAnswer = ref({});
const testBackend = async () => {
  const url = "http://localhost:4200/api/health";
  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`Response status: ${response.status}`);
    }
    const json = await response.json();
    console.log(json);
    backEndAnswer.value = json;
    showConfirm.value = !showConfirm.value;
  } catch (error) {
    console.error(error.message);
  }
};
</script>
