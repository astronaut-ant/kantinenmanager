<template>
  <h1 class="text-center mt-5 text-pink">Frontend ... under construction</h1>
  <div class="d-flex justify-center mt-5 ga-5">
    <v-btn class="text-dark" to="../testroute">testRoute#</v-btn>
    <v-btn @click="testBackend" class="bg-pink">Backend check</v-btn>
  </div>
  <div v-if="showConfirm" class="d-flex justify-center">
    <h3>{{ backEndAnswer }}</h3>
    <v-icon
      class="mt-6"
      color="success"
      icon="mdi-check-circle-outline"
      size="128"
    >
    </v-icon>
  </div>
</template>

<script setup>
const showConfirm = ref(false);
const backEndAnswer = ref("");
const testBackend = async () => {
  const url = "https://dummyjson.com/products";
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
