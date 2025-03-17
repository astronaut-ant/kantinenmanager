<template>
  <v-dialog
    :model-value="props.showBestellformular"
    max-width="800"
    :persistent="true"
    :no-click-animation="true"
  >
    <v-card>
      <h3 class="text-center mt-5 mb-4">Gruppe: {{ props.group }}</h3>
      <v-row justify="end">
        <v-icon
          v-if="!orderStop"
          size="x-large"
          class="text-center bg-primary me-10 mt-n10 rounded pa-5"
          >mdi-note-edit-outline</v-icon
        >
        <v-icon
          v-if="orderStop"
          size="x-large"
          class="text-center bg-red me-10 mt-10 rounded pa-5"
          >mdi-send-lock</v-icon
        >
      </v-row>
      <div>
        <h2 class="text-center mt-10 mb-2">Bestellung für {{ props.date }}</h2>
      </div>
      <CustomAlert
        v-if="showRestoreAlert"
        class="w-75"
        color="red"
        icon="$error"
        text="Frist für Vorbestellungen abgelaufen: Ihre letzten Änderungen wurden nicht übernommen"
      />
      <v-card-text>
        <v-data-table-virtual
          @change="updateProgress"
          :hover="true"
          :fixed-header="true"
          :height="300"
          :items="items"
          item-key="name"
          :headers="headers"
          v-model:sort-by="sortBy"
        >
          <template v-slot:item.done="{ item }">
            <v-icon v-model="item.done">{{
              item.done ? "mdi-check" : ""
            }}</v-icon>
          </template>

          <template v-slot:item.hauptgericht1="{ item }">
            <v-checkbox-btn
              @change="orderHauptgericht1(item)"
              :readonly="orderStop"
              true-icon="mdi-circle"
              false-icon="mdi-circle"
              color="primary"
              v-model="item.hauptgericht1"
            ></v-checkbox-btn>
          </template>

          <template v-slot:item.hauptgericht2="{ item }">
            <v-checkbox-btn
              @change="orderHauptgericht2(item)"
              :readonly="orderStop"
              true-icon="mdi-circle"
              false-icon="mdi-circle"
              color="red"
              v-model="item.hauptgericht2"
            ></v-checkbox-btn>
          </template>

          <template v-slot:item.salat="{ item }">
            <v-checkbox-btn
              @change="orderSalat(item)"
              :readonly="orderStop"
              true-icon="mdi-circle"
              false-icon="mdi-circle"
              color="success"
              v-model="item.salat"
            ></v-checkbox-btn>
          </template>

          <template v-slot:item.keinEssen="{ item }">
            <v-checkbox-btn
              @change="orderKeinEssen(item)"
              :readonly="orderStop"
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
      <v-card-actions class="me-4 mb-2">
        <v-spacer></v-spacer>

        <v-btn text="Abbrechen" @click="close">{{
          orderStop ? "Schließen" : "Abbrechen"
        }}</v-btn>
        <v-btn
          v-if="!orderStop"
          class="bg-primary elevation-7"
          text="Speichern"
          @click="save"
        ></v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
// import { toRaw } from "vue";

const items = ref([]);

const orderStop = ref(false);
const showRestoreAlert = ref(false);

// console.log("test");

const headers = ref([
  {
    title: "Mitarbeiter",
    value: "name",
    key: "mitarbeiter",
  },
  { title: " ", value: "done", minWidth: "15em" },
  { title: "Menü 1", value: "hauptgericht1", nowrap: true },
  { title: "Menü 2", value: "hauptgericht2", nowrap: true },
  { title: "Salat", value: "salat", nowrap: true },
  { title: "Nichts", value: "keinEssen", nowrap: true },
]);

const sortBy = ref([{ key: "mitarbeiter", order: "asc" }]);
const props = defineProps([
  "showBestellformular",
  "date",
  "orders",
  "group",
  "stopHour",
]);
const emit = defineEmits(["close", "save"]);
const close = () => {
  emit("close");
};

let initials;
let clone = [];
const loadData = () => {
  console.log("loading");
  items.value = [];
  console.log("props.orders", props.orders);
  if (props.orders != undefined) {
    props.orders.forEach((order) => {
      items.value.push(order);
    });
    initials = JSON.stringify(items.value);
    // toRaw(items.value).forEach((item) => {
    //   initials.push(item);
    // });
    console.log("items", items.value);
    console.log("initials", initials);
  }
};
loadData();

const save = () => {
  if (!checkOrderStop(props.stopHour)) {
    emit("save", items.value, props.date, props.group);
  } else {
    //HACK for Restoring old Data if trying to edit before Stophour and safe after Stophour
    items.value = [];
    JSON.parse(initials).forEach((initial) => {
      items.value.push(initial);
      console.log(initial);
    });
    console.log("items", items.value);
    console.log("initials", initials);
    orderStop.value = true;
    showRestoreAlert.value = true;
    updateProgress();
  }
};

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

const checkOrderStop = (limit) => {
  const today = new Date();
  if (
    props.date === today.toISOString().split("T")[0] &&
    today.getHours() >= limit
  ) {
    return true;
  }
  return false;
};
updateProgress();
if (checkOrderStop(props.stopHour)) {
  orderStop.value = true;
}
</script>
