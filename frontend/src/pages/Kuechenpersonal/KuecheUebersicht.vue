<template>
  <NavbarKueche :breadcrumbs = '[{"title": "Heutige Bestellungen"}]'/>
  <h1 class="text-center mt-5">Heutige Bestellungen</h1>
  <v-container class="pa-4">
    <v-row>
      <v-col cols="4">
        <v-card class="text-center">
          <v-card-title>Rotes Hauptgericht</v-card-title>
          <v-card-text>
            <v-icon color="red" size="36">mdi-circle</v-icon>
            {{ orderCount.blau }}
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="4">
        <v-card class="text-center">
          <v-card-title>Blaues Hauptgericht</v-card-title>
          <v-card-text>
            <v-icon color="primary" size="36">mdi-circle</v-icon>
            {{ orderCount.rot }}
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="4">
        <v-card class="text-center">
          <v-card-title>Salat</v-card-title>
          <v-card-text>
            <v-icon color="green" size="36">mdi-leaf</v-icon>
            {{ orderCount.salad_option }}
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
  <v-data-table-virtual
    :hover="true"
    :fixed-header="true"
    :height="tableHeight"
    :items="tableData"
    item-key="id"
    :headers="headers"
    :sort-by="sortBy"
  >

    <template v-slot:item.main_dish="{ item }">
      <v-icon
        :color="item.main_dish === 'rot' ? 'red' : item.main_dish === 'blau' ? 'primary' : 'grey'"
        size="24"
      >
        mdi-circle
      </v-icon>
    </template>

    <template v-slot:item.salad_option="{ item }">
      <v-icon
        :color="item.salad_selected ? 'green' : 'grey'"
        size="24"
      >
        mdi-circle
      </v-icon>
    </template>

    <template v-slot:item.handed_out="{ item }">
      <v-btn
        :icon="item.handed_out ? 'mdi-check' : 'mdi-close'"
        density="compact"
        @click="openConfirmDialog(item)"
      ></v-btn>
    </template>
  </v-data-table-virtual>

  <v-dialog v-model="dialog" max-width="400px" persistent>
    <v-card>
      <v-card-title class="headline">Bestätigung</v-card-title>
      <v-card-text>
        Möchten Sie den Status Ausgabe der Bestellung wirklich ändern?
      </v-card-text>
      <v-card-actions>
        <v-btn color="red darken-1" text @click="closeConfirmDialog">Abbrechen</v-btn>
        <v-btn color="green darken-1" text @click="confirmChange">Bestätigen</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import axios from "axios";

const orders = ref([]);
const employees = ref([]);
const tableData = ref([]);
const dialog = ref(false);
const itemToConfirm = ref(null);
const orderCount = ref({
  blau: 0,
  rot: 0,
  salad_option: 0,
});

const sortBy = [{ key: 'group_name', order: 'asc' }]

const tableHeight = computed(() => {
  const headerHeight = 80; // Höhe der Navbar
  return window.innerHeight - headerHeight - 100 + 'px';
})

const headers = ref([
  { title: "Mitarbeiter", value: "full_name", key: "full_name" },
  { title: "Gruppe", value: "group_name" },
  { title: "Hauptgericht", value: "main_dish" },
  { title: "Salat", value: "salad_option" },
  { title: "Ausgehändigt", value: "handed_out" },
]);

// Daten laden und verbinden
onMounted(() => {
  axios
    .get(import.meta.env.VITE_API + "/api/daily-orders", { withCredentials: true })
    .then((response) => {
      orders.value = response.data;
      console.log(orders.value);
      updateTableData();
    })
    .catch((err) => console.error(err));

  axios
    .get(import.meta.env.VITE_API + "/api/employees", { withCredentials: true })
    .then((response) => {
      employees.value = response.data;
      console.log(employees.value);
      updateTableData();
    })
    .catch((err) => console.error(err));

  axios
    .get(import.meta.env.VITE_API + "/api/daily-orders/counted", { withCredentials: true })
    .then((response) => {
      orderCount.value = response.data[0] || { blau: 0, rot: 0, salad_option: 0 };
      console.error(orderCount.value);
    })
    .catch((err) => console.error(err));
});

// Daten zusammenführen
const updateTableData = () => {
  if (orders.value.length === 0 || employees.value.length === 0) return;

  tableData.value = orders.value.map((order) => {
    const employee = employees.value.find((emp) => emp.id === order.person_id);
    return {
      id: order.id,
      full_name: `${employee?.first_name || ""} ${employee?.last_name || ""}`,
      group_name: employee?.group?.group_name || "Keine Gruppe",
      main_dish: order.main_dish || "Keine Angabe",
      main_dish_selected: order.main_dish === "rot",
      salad_selected: order.salad_option,
      handed_out: order.handed_out,
    };
  });
}

const openConfirmDialog = (item) => {
  itemToConfirm.value = item;
  dialog.value = true;
};
const confirmChange = () => {
  axios
    .put(import.meta.env.VITE_API + `/api/daily-orders/${itemToConfirm.value.id}`,
    {"handed_out": !itemToConfirm.value.handed_out},
    { withCredentials: true })
    .then(() => {
      itemToConfirm.value.handed_out = !itemToConfirm.value.handed_out;
      closeConfirmDialog();
    })
    .catch((err) => {
      console.log(err)
    })
};
const closeConfirmDialog = () => {
  itemToConfirm.value = null;
  dialog.value = false
}
</script>
