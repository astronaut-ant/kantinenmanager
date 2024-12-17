<template>
  <v-sheet
    class="rounded-circle me-n5 elevation-15"
    :class="formattedColor"
    height="15vw"
    width="15vw"
  ></v-sheet>
  <v-sheet
    class="rounded-circle ms-n5 bg-green elevation-15"
    height="15vw"
    width="15vw"
  ></v-sheet>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps(["color"]);
const formattedColor = computed(() => {
  return "bg-" + props.color;
});
</script>
