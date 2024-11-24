<template>
  <v-sheet
    class="rounded-circle opacity-70"
    :class="formattedColor"
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
