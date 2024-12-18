<template>
  <NavbarKueche />
  <h1 class="text-center mt-5">Heutige Bestellungen</h1>
  <h4 class="mb-10 mt-5">{{ ordersCount }}</h4>
  <div class="mb-3 border pa-5" v-for="order in orders">
    <h3 class="mb-2">Datum: {{ order.date }}</h3>
    <p>Ausgehändigt: {{ order.handed_out }}</p>
    <p>BestellNr.: {{ order.id }}</p>
    <p>StandortNr.: {{ order.location_id }}</p>
    <p>Hauptgricht: {{ order.main_dish }}</p>
    <p>Nichts: {{ order.nothing }}</p>
    <p>PersonalNr.: {{ order.person_id }}</p>
    <p>Salat: {{ order.salad_option }}</p>
  </div>
</template>

<script setup>
import axios from "axios";

const ordersCount = ref();
const orders = ref("");

axios
  .get(import.meta.env.VITE_API + "/api/daily-orders", {
    withCredentials: true,
  })
  .then((response) => {
    orders.value = response.data;
  })
  .catch((err) => console.log(err));

axios
  .get(import.meta.env.VITE_API + "/api/daily-orders/counted", {
    withCredentials: true,
  })
  .then((response) => {
    ordersCount.value = response.data;
  })
  .catch((err) => console.log(err));
</script>
