<template>
  <v-dialog v-model="dialog" width="400">
    <template v-slot:activator="{ props: activatorProps }">
      <div class="text-start">
        <v-btn
          @click="getData"
          v-bind="activatorProps"
          color="blue-grey"
          variant="text"
        >
          <v-badge
            dot
            class="me-4"
            :color="showDailyOrderReminder ? 'red' : 'transparent'"
          >
            <v-icon>mdi-calendar-today-outline</v-icon> </v-badge
          >Heutige Bestellung
        </v-btn>
      </div>
    </template>

    <v-card max-height="800" class="mx-auto px-4" color="blue-grey-lighten-5">
      <v-card-text>
        <h2 class="ms-n1 mt-2 mb-6 text-blue-grey font-weight-bold">
          <v-icon class="me-2 text-blue-grey">
            mdi-calendar-today-outline</v-icon
          >
          Heutige Bestellung
        </h2>
        <h3 v-if="!dailyOrderExists" class="text-blue-grey">
          Für das heutige Datum liegen keine Bestellungen vor!
        </h3>
        <p v-if="dailyOrderExists" class="mb-2 text-blue-grey">
          Datum:
          <span class="font-weight-bold">{{ dailyFoodObject.date }}</span>
        </p>
        <p v-if="dailyOrderExists" class="mb-2 text-blue-grey">
          Standort: <span class="font-weight-bold">{{ locationName }}</span>
        </p>
        <div v-if="dailyOrderExists" class="mb-3 text-blue-grey">
          <span>Menü: </span>
          <v-icon
            class="me-n3"
            v-if="
              dailyFoodObject.main_dish === 'rot' ||
              dailyFoodObject.main_dish === 'blau'
            "
            :class="
              dailyFoodObject.main_dish == 'rot' ? 'text-red' : 'text-primary'
            "
            >mdi-circle</v-icon
          >
          <v-icon v-if="dailyFoodObject.salad_option" class="text-success"
            >mdi-circle</v-icon
          >
        </div>
        <v-divider
          v-if="dailyOrderExists"
          class="mb-3 text-blue-grey"
        ></v-divider>
        <p v-if="dailyOrderExists" class="text-blue-grey">
          Status:
          <span
            class="font-weight-bold"
            :class="dailyFoodObject.handed_out ? 'text-success' : 'text-red'"
            >{{
              dailyFoodObject.handed_out ? "Ausgegeben" : "Ausstehend"
            }}</span
          >
        </p>
      </v-card-text>
      <v-card-actions class="pe-5">
        <v-btn
          class="mb-3 mt-n1"
          color="blue-grey"
          text="Zurück"
          variant="tonal"
          @click="close"
        ></v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
const dialog = ref(false);
const close = () => {
  dialog.value = false;
};
const showDailyOrderReminder = ref(false);
const dailyOrderExists = ref(false);
const dailyFoodObject = ref({});
const locationName = ref();

import axios from "axios";
const getData = () => {
  axios
    .get(import.meta.env.VITE_API + "/api/daily-orders/own", {
      withCredentials: true,
    })
    .then((response) => {
      dailyFoodObject.value = response.data;
      console.log("dfo", dailyFoodObject.value);
      dailyOrderExists.value = true;
      console.log("dailyFoodObject", dailyFoodObject.value);
      if (!dailyFoodObject.value.handed_out) {
        showDailyOrderReminder.value = true;
      } else {
        showDailyOrderReminder.value = false;
      }
      getLocationName();
    })
    .catch((err) => {
      dailyOrderExists.value = false;
      console.log(err);
    });
};

const getLocationName = () => {
  axios
    .get(
      import.meta.env.VITE_API +
        `/api/locations/${dailyFoodObject.value.location_id}`,
      {
        withCredentials: true,
      }
    )
    .then((response) => {
      locationName.value = response.data.location_name;
    })
    .catch((err) => {
      console.log(err);
    });
};

getData();
const polling = setInterval(getData, 10000);
onUnmounted(() => clearInterval(polling));
</script>
