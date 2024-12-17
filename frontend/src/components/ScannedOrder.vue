<template>
  <v-container
    min-height="100%"
    class="bg-white d-flex flex-column justify-space-around ga-2 elevation-7 rounded"
  >
    <!-- <p>{{ props.data[0].rawValue }}</p> -->
    <v-container
      max-height="50"
      min-width="30"
      class="d-flex justify-center mt-2"
    >
      <DoubleCircle v-if="isHauptgericht1Salat" color="primary" />
      <DoubleCircle v-if="isHauptgericht2Salat" color="red" />
      <SingleCircle v-if="isHauptgericht1" color="primary" />
      <SingleCircle v-if="isHauptgericht2" color="red" />
    </v-container>
    <div class="d-flex justify-center">
      <v-btn
        width="25vw"
        height="5vw"
        class="bg-blue-grey mt-10 elevation-10"
        @click="$emit('close')"
      >
        <v-icon class="text-xs-h5 text-sm-h4 text-md-h3 text-lg-h2 align-center"
          >mdi-check</v-icon
        >
      </v-btn>
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
