<template>
  <v-dialog color="" v-model="dialog" max-width="800">
    <template v-slot:activator="{ props: activatorProps }">
      <div class="text-start">
        <v-btn
          @click="getData"
          variant="text"
          v-bind="activatorProps"
          class="text-blue-grey"
          ><v-icon class="me-4">mdi-calendar-edit-outline</v-icon>Meine
          Bestellungen</v-btn
        >
      </div>
    </template>

    <v-card max-height="800" class="mx-auto px-4" color="blue-grey-lighten-5">
      <v-card-text>
        <h2 class="mt-4 mb-6 text-blue-grey font-weight-bold">
          <v-icon class="me-4 text-blue-grey">
            mdi-calendar-edit-outline</v-icon
          >
          Meine Bestellungen
        </h2>
        <UserNewFoodOrder
          :person-id="props.personId"
          :location-items="locationItems"
          @ordered="getData"
        />
        <div>
          <v-data-table-virtual
            v-model:sort-by="sortBy"
            :hover="true"
            :headers="headers"
            :items="items"
            item-key="date"
            class="bg-transparent text-blue-grey"
          >
            <template v-slot:item.date="{ item }">
              <div class="me-5">{{ item.date }}</div>
            </template>
            <template v-slot:item.mainDish="{ item }">
              <div>
                <v-icon
                  v-if="item.mainDish !== 0"
                  size="large"
                  :color="item.mainDish == 1 ? 'primary' : 'red'"
                >
                  mdi-circle</v-icon
                >
                <v-icon v-else size="large" color="blue-grey">
                  mdi-close-circle-outline</v-icon
                >
              </div>
            </template>

            <template v-slot:item.salad="{ item }">
              <v-icon
                size="large"
                :color="item.salad ? 'success' : 'blue-grey'"
                >{{
                  item.salad ? "mdi-circle" : "mdi-close-circle-outline"
                }}</v-icon
              >
            </template>

            <template v-slot:item.actions="{ item }">
              <div class="d-flex justify-space-between ga-2 me-n4 mb-2">
                <v-btn variant="tonal" color="primary" class="mt-2"
                  ><v-icon>mdi-lead-pencil</v-icon></v-btn
                >
                <v-btn variant="tonal" color="red" class="mt-2"
                  ><v-icon>mdi-trash-can-outline</v-icon></v-btn
                >
              </div>
            </template>
          </v-data-table-virtual>
        </div>
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
import axios from "axios";
import UserNewFoodOrder from "./UserNewFoodOrder.vue";

const dialog = ref(false);
const form = ref(false);
const orders = ref([]);
const locationItems = ref([]);
const locationTable = {};
const sortBy = ref([{ key: "date", order: "desc" }]);

const headers = ref([
  { title: "Datum", align: "start", key: "date" },
  { title: "Standort", align: "start", key: "location" },
  {
    title: "Hauptgericht",
    align: "start",
    key: "mainDish",
  },
  { title: "Salat", align: "start", key: "salad" },
  {
    title: "Aktionen",
    align: "start",
    key: "actions",
    sortable: false,
  },
]);

const items = ref([]);

const close = () => {
  dialog.value = false;
};
const props = defineProps(["personId"]);

const getData = () => {
  orders.value.length = 0;
  locationItems.value.length = 0;
  items.value.length = 0;
  locationTable.value = {};
  axios
    .get(import.meta.env.VITE_API + "/api/locations", { withCredentials: true })
    .then((response) => {
      response.data.forEach((locationobject) => {
        locationItems.value.push({
          title: locationobject.location_name,
          value: locationobject.id,
        }),
          (locationTable[locationobject.id] = locationobject.location_name);
      });
      console.log(locationItems.value);
      getOrders();
    })
    .catch((err) => console.log(err));
};

const getOrders = () => {
  axios
    .get(
      import.meta.env.VITE_API + `/api/pre-orders?person-id=${props.personId}`,
      {
        withCredentials: true,
      }
    )
    .then((response) => {
      orders.value = response.data;
      orders.value.forEach((order) => {
        order.location_name = locationTable[order.location_id];
        if (order.main_dish == "blau") {
          order.main_dish = 1;
        } else if (order.main_dish == "rot") {
          order.main_dish = 2;
        } else {
          order.main_dish = 0;
        }
        items.value.push({
          date: order.date,
          location: order.location_name,
          mainDish: order.main_dish,
          salad: order.salad_option,
        });
      });
      console.log("Orders", orders.value);
    })
    .catch((err) => console.log(err));
};
</script>
