<template>
  <v-container
    min-height="100%"
    class="bg-grey-lighten-3 d-flex flex-column justify-space-around ga-2 elevation-7 rounded"
  >
    <!-- <p>{{ props.data[0].rawValue }}</p> -->
    <div class="d-flex justify-center mt-2">
      <DoubleCircle v-if="isHauptgericht1Salat" color="primary" />
      <DoubleCircle v-if="isHauptgericht2Salat" color="red" />
      <SingleCircle v-if="isHauptgericht1" color="primary" />
      <SingleCircle v-if="isHauptgericht2" color="red" />
    </div>
    <div class="d-flex justify-center">
      <v-btn class="bg-white w-50" @click="$emit('close')"
        ><h1 class="text-grey-darken-2">
          <v-icon class="size">mdi-check</v-icon>
        </h1></v-btn
      >
    </div>
  </v-container>
</template>

<script setup>
import DoubleCircle from "./DoubleCircle.vue";
import SingleCircle from "./SingleCircle.vue";

const dialog = ref(true);
const props = defineProps(["data"]);
const isHauptgericht1Salat =
  props.data[0].rawValue == "Hauptgericht 1 mit Salat";
const isHauptgericht2Salat =
  props.data[0].rawValue == "Hauptgericht 2 mit Salat";
const isHauptgericht1 = props.data[0].rawValue == "Hauptgericht 1";
const isHauptgericht2 = props.data[0].rawValue == "Hauptgericht 2";
</script>
