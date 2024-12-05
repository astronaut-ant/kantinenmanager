<template>
  <v-dialog
    :model-value="props.showBestellformular"
    max-width="500"
    :persistent="true"
    :no-click-animation="true"
  >
    <v-card :title="'Bestellung für ' + props.date">
      <v-card-text>
        <v-data-table :items="items"></v-data-table>
      </v-card-text>

      <v-card-actions>
        <v-spacer></v-spacer>

        <v-btn text="Schließen" @click="close"></v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
const items = [
  {
    name: "African Elephant",
    species: "Loxodonta africana",
    diet: "Herbivore",
    habitat: "Savanna, Forests",
  },
  {
    name: "African Elephant",
    species: "Loxodonta africana",
    diet: "Herbivore",
    habitat: "Savanna, Forests",
  },
  {
    name: "African Elephant",
    species: "Loxodonta africana",
    diet: "Herbivore",
    habitat: "Savanna, Forests",
  },
  {
    name: "African Elephant",
    species: "Loxodonta africana",
    diet: "Herbivore",
    habitat: "Savanna, Forests",
  },
  {
    name: "African Elephant",
    species: "Loxodonta africana",
    diet: "Herbivore",
    habitat: "Savanna, Forests",
  },
  {
    name: "African Elephant",
    species: "Loxodonta africana",
    diet: "Herbivore",
    habitat: "Savanna, Forests",
  },
  // ... more items
];

const props = defineProps(["showBestellformular", "date"]);
const emit = defineEmits(["close", "save"]);
const close = () => {
  emit("close");
};
</script>
