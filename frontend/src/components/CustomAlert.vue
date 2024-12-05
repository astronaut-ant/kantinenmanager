<template>
  <v-container class="mt-7 border pa-0">
    <v-alert
      :color="props.color"
      :icon="props.icon"
      :text="props.text"
    ></v-alert>
  </v-container>
</template>

<script setup>
const props = defineProps(["text", "color", "icon"]);
</script>
