<template>
  <v-dialog
    :model-value="props.showBestellformular"
    max-width="800"
    :persistent="true"
    :no-click-animation="true"
  >
    <v-card>
      <h2 class="text-center mt-5 mb-2">Bestellung für {{ props.date }}</h2>
      <h3 class="text-center mt-1 mb-2">Gruppe: {{ props.group }}</h3>
      <v-card-text>
        <v-data-table-virtual
          @change="updateProgress"
          :hover="true"
          :fixed-header="true"
          :height="300"
          :items="items"
          item-key="name"
          :headers="headers"
        >
          <template v-slot:item.done="{ item }">
            <v-icon v-model="item.done">{{
              item.done ? "mdi-check" : ""
            }}</v-icon>
          </template>

          <template v-slot:item.hauptgericht1="{ item }">
            <v-checkbox-btn
              @change="orderHauptgericht1(item)"
              true-icon="mdi-circle"
              false-icon="mdi-circle"
              color="primary"
              v-model="item.hauptgericht1"
            ></v-checkbox-btn>
          </template>

          <template v-slot:item.hauptgericht2="{ item }">
            <v-checkbox-btn
              @change="orderHauptgericht2(item)"
              true-icon="mdi-circle"
              false-icon="mdi-circle"
              color="red"
              v-model="item.hauptgericht2"
            ></v-checkbox-btn>
          </template>

          <template v-slot:item.salat="{ item }">
            <v-checkbox-btn
              @change="orderSalat(item)"
              true-icon="mdi-circle"
              false-icon="mdi-circle"
              color="success"
              v-model="item.salat"
            ></v-checkbox-btn>
          </template>

          <template v-slot:item.keinEssen="{ item }">
            <v-checkbox-btn
              @change="orderKeinEssen(item)"
              color="black"
              true-icon="mdi-circle"
              false-icon="mdi-circle"
              class="rounded-circle"
              v-model="item.keinEssen"
            ></v-checkbox-btn>
          </template>
        </v-data-table-virtual>
        <v-progress-linear
          v-model="progress"
          :color="progress == 100 ? 'success' : 'red'"
          height="25"
          class="mt-10"
          rounded
          rounded-bar
        >
          <strong class="text-white">{{ progressText }}</strong>
        </v-progress-linear>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>

        <v-btn text="Abbrechen" @click="close"></v-btn>
        <v-btn
          class="bg-primary elevation-7"
          text="Speichern"
          @click="save"
        ></v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { onMounted } from "vue";

const items = ref([]);

console.log("test");

const headers = ref([
  { title: "Mitarbeiter", value: "name" },
  { title: "", value: "done", minWidth: "15em" },
  { title: "Menü 1", value: "hauptgericht1", nowrap: true },
  { title: "Menü 2", value: "hauptgericht2", nowrap: true },
  { title: "Salat", value: "salat", nowrap: true },
  { title: "Nichts", value: "keinEssen", nowrap: true },
]);
const props = defineProps(["showBestellformular", "date", "orders", "group"]);
const emit = defineEmits(["close", "save"]);
const close = () => {
  emit("close");
};

const save = () => {
  emit("save", items.value, props.date, props.group);
};
props.orders.forEach((order) => {
  items.value.push(order);
});

//Progress Bar
const totalItems = items.value.length;
const updateProgress = () => {
  const calcFilled = () => {
    let summation = 0;
    items.value.forEach((item) => {
      if (
        item.hauptgericht1 ||
        item.hauptgericht2 ||
        item.salat ||
        item.keinEssen
      ) {
        item.done = true;
        summation++;
      } else {
        item.done = false;
      }
    });
    return summation;
  };
  progressText.value = calcFilled() + " / " + totalItems;
  if (calcFilled === 0) {
    progress.value = 0;
  } else {
    progress.value = Math.round((calcFilled() / totalItems) * 100);
  }
};
const progress = ref(0);
const progressText = ref(0 + " / " + items.value.length);

//Order Rules
const orderHauptgericht1 = (item) => {
  if (item.hauptgericht1) {
    item.hauptgericht2 = false;
    item.keinEssen = false;
  }
};

const orderHauptgericht2 = (item) => {
  if (item.hauptgericht2) {
    item.hauptgericht1 = false;
    item.keinEssen = false;
  }
};

const orderSalat = (item) => {
  if (item.salat) {
    item.keinEssen = false;
  }
};

const orderKeinEssen = (item) => {
  if (item.keinEssen) {
    item.hauptgericht1 = false;
    item.hauptgericht2 = false;
    item.salat = false;
  }
};

onMounted(() => {
  updateProgress();
});
</script>
