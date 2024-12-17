<template>
  <v-container
    min-height="100%"
    class="bg-white d-flex flex-column justify-space-around ga-2 elevation-7 rounded"
  >
    <!-- <p>{{ props.data[0].rawValue }}</p> -->
    <v-container
      max-height="50"
      min-width="30"
      class="d-flex justify-center mt-2 mb-10"
    >
      <DoubleCircle v-if="maindishBlue && salad" color="primary" />
      <DoubleCircle v-if="maindishRed && salad" color="red" />
      <SingleCircle v-if="maindishBlue && !salad" color="primary" />
      <SingleCircle v-if="maindishRed && !salad" color="red" />
      <SingleCircle
        v-if="salad && !maindishRed && !maindishBlue"
        color="success"
      />
      <v-icon v-if="!accepted" color="red" size="15vw"
        >mdi-hand-back-left</v-icon
      >
    </v-container>
    <div class="d-flex justify-center mt-15">
      <v-btn
        width="25vw"
        height="5vw"
        class="bg-blue-grey elevation-10"
        @click="$emit('close')"
      >
        <v-icon
          class="text-xs-h5 text-sm-h4 text-md-h3 text-lg-h2 align-center"
          >{{ accepted ? "mdi-check" : "mdi-close" }}</v-icon
        >
      </v-btn>
    </div>
  </v-container>
</template>

<script setup>
import DoubleCircle from "./DoubleCircle.vue";
import SingleCircle from "./SingleCircle.vue";
import axios from "axios";

const props = defineProps(["data"]);
const scannedId = props.data[0].rawValue;
let order;

const maindishRed = ref(false);
const maindishBlue = ref(false);
const salad = ref(false);
const accepted = ref(true);

const redAndGreen = () => {
  maindishRed.value = true;
  maindishBlue.value = false;
  salad.value = true;
  accepted.value = true;
};
const blueAndGreen = () => {
  maindishRed.value = false;
  maindishBlue.value = true;
  salad.value = true;
  accepted.value = true;
};
const red = () => {
  maindishRed.value = true;
  maindishBlue.value = false;
  salad.value = false;
  accepted.value = true;
};
const blue = () => {
  maindishRed.value = false;
  maindishBlue.value = true;
  salad.value = false;
  accepted.value = true;
};
const green = () => {
  maindishRed.value = false;
  maindishBlue.value = false;
  salad.value = true;
  accepted.value = true;
};
const forbidden = () => {
  maindishRed.value = false;
  maindishBlue.value = false;
  salad.value = false;
  accepted.value = false;
};
const handOut = (order) => {
  console.log("putting");
  axios
    .put(
      `http://localhost:4200/api/daily-orders/${order.id}`,
      { handed_out: true },
      { withCredentials: true }
    )
    .then(console.log("test"))
    .catch((err) => {
      console.log(err);
    });
};

axios
  .get(`http://localhost:4200/api/daily-orders/person/${scannedId}`, {
    withCredentials: true,
  })
  .then((response) => {
    const order = response.data;
    console.log(order);
    if (order.handed_out) {
      console.log("1");
      forbidden();
    } else if (order.salad_option && order.main_dish === "rot") {
      console.log("2");
      redAndGreen();
      handOut(order);
    } else if (order.salad_option && order.main_dish === "blau") {
      console.log("3");
      blueAndGreen();
      handOut(order);
    } else if (order.salad_option) {
      console.log("4");
      green();
      handOut(order);
    } else if (!order.salad_option && order.main_dish === "rot") {
      console.log("5");
      red();
      handOut(order);
    } else if (!order.salad_option && order.main_dish === "blau") {
      console.log("6");
      blue();
      handOut(order);
    } else {
      console.log("7");
      forbidden();
    }
  })

  .catch((err) => {
    forbidden();
  });

// })

// })
</script>
