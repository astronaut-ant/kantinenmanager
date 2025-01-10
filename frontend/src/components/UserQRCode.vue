<template>
  <v-dialog color="" v-model="dialog" max-width="800">
    <template v-slot:activator="{ props: activatorProps }">
      <div class="text-start">
        <v-btn variant="text" v-bind="activatorProps" class="text-blue-grey"
          ><v-icon class="me-4">mdi-qrcode</v-icon>Mein QR-Code</v-btn
        >
      </div>
    </template>

    <v-card max-height="800" class="mx-auto px-10" color="blue-grey-lighten-5">
      <v-card-text>
        <h2 class="mt-5 mb-6 text-blue-grey font-weight-bold">
          <v-icon class="me-4 text-blue-grey">
            mdi-calendar-edit-outline</v-icon
          >
          Meine Bestellungen
        </h2>
        <v-btn class="mt-2 mb-5" color="primary">
          <v-icon class="me-2">mdi-plus</v-icon>Neue Bestellung aufgeben
        </v-btn>
        <div>
          <v-data-table-virtual
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
        <v-btn @click="close" class="bg-primary mb-2 mt-2" variant="elevated"
          >Schließen</v-btn
        >
      </v-card-actions>

      <!-- <div class="mt-5">
        <v-date-input
          :allowed-dates="[new Date('1/25/25')]"
          label="Select a date"
          prepend-icon=""
          prepend-inner-icon="$calendar"
          variant="solo"
        ></v-date-input>
      </div> -->
    </v-card>
  </v-dialog>
</template>

<script setup>
import axios from "axios";

const dialog = ref(false);
const form = ref(false);
const close = () => {
  dialog.value = false;
};
</script>

<!-- Dummy -->
<script>
export default {
  data() {
    return {
      headers: [
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
      ],
      items: [
        {
          date: "2025-01-02",
          location: "W3",
          mainDish: 0,
          salad: true,
        },
        {
          date: "2025-01-04",
          location: "W5",
          mainDish: 2,
          salad: false,
        },
      ],
    };
  },
};
</script>
