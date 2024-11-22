<template>
  <v-sheet
    class="rounded-circle me-n5 opacity-70"
    :class="formattedColor"
    height="100"
    width="100"
  ></v-sheet>
  <v-sheet
    class="rounded-circle ms-n5 bg-green opacity-70"
    height="100"
    width="100"
  ></v-sheet>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps(["color"]);
const formattedColor = computed(() => {
  return "bg-" + props.color;
});
</script>
