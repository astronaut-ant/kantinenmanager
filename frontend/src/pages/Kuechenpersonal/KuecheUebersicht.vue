<template>
  <NavbarKueche />
  <h1 class="text-center mt-5">Heutige Bestellungen</h1>
  <v-data-table-virtual
    :hover="true"
    :fixed-header="true"
    :height="300"
    :items="tableData"
    item-key="id"
    :headers="headers"
    :sort-by="sortBy"
  >
    <template v-slot:item.done="{ item }">
      <v-icon>{{ item.handed_out ? "mdi-check" : "" }}</v-icon>
    </template>

    <template v-slot:item.main_dish="{ item }">
      <v-checkbox-btn
        :readonly="orderStop"
        true-icon="mdi-circle"
        false-icon="mdi-circle"
        color="primary"
        v-model="item.main_dish_selected"
      ></v-checkbox-btn>
    </template>

    <template v-slot:item.salad_option="{ item }">
      <v-checkbox-btn
        :readonly="orderStop"
        true-icon="mdi-circle"
        false-icon="mdi-circle"
        color="success"
        v-model="item.salad_selected"
      ></v-checkbox-btn>
    </template>

    <template v-slot:item.handed_out="{ item }">
      <v-checkbox-btn
        :readonly="orderStop"
        true-icon="mdi-circle"
        false-icon="mdi-circle"
        color="red"
        v-model="item.handed_out"
      ></v-checkbox-btn>
    </template>
  </v-data-table-virtual>
</template>

<script setup>
import axios from "axios";
import { ref, computed, onMounted } from "vue";

const orders = ref([]);
const employees = ref([]);
const tableData = ref([]);

const sortBy = [{ key: 'group_name', order: 'asc' }]

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
});

// Daten zusammenführen
function updateTableData() {
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
</script>
