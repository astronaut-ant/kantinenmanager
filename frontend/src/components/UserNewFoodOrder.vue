<template>
  <v-dialog v-model="dialog" width="400">
    <template v-slot:activator="{ props: activatorProps }">
      <v-btn
        @click="stepperValue = 1"
        v-bind="activatorProps"
        class="mt-2 mb-5"
        color="primary"
      >
        <v-icon class="me-2">mdi-plus</v-icon>Neue Bestellung aufgeben
      </v-btn>
    </template>

    <div class="d-flex justify-center">
      <v-stepper
        v-model="stepperValue"
        prev-text="Zurück"
        class="test"
        :width="400"
        color="primary"
        elevation="24"
        bg-color="#ECEFF1"
        :items="['Datum', 'Standort', 'Menü']"
      >
        <template v-slot:item.1>
          <v-card
            class="test"
            color="#ECEFF1"
            title="Datum der Bestellung"
            flat
          >
            <v-container>
              <v-row justify="center">
                <v-date-picker
                  @update:model-value="step1Valid = false"
                  v-model="dateSelection"
                  elevation="2"
                  class="test"
                  height="350"
                  color="primary"
                  bg-color="#ECEFF1"
                  :first-day-of-week="1"
                  :hide-header="true"
                >
                </v-date-picker>
              </v-row>
            </v-container>
          </v-card>
        </template>

        <template v-slot:item.2>
          <v-card
            color="#ECEFF1"
            class="text-blue-grey"
            title="Standort der Bestellung"
            flat
          >
            <v-select
              @update:model-value="step2Valid = false"
              v-model="locationSelection"
              placeholder="Standort auswählen"
              :items="locationItems"
              color="primary"
              variant="solo"
            ></v-select>
          </v-card>
        </template>

        <template v-slot:item.3>
          <v-card class="text-blue-grey" title="Menü" color="#ECEFF1" flat>
            <div class="d-flex">
              <v-select
                clearable
                persistent-clear
                v-model="foodChoice"
                @update:model-value="checkForOneMainDish()"
                color="blue-grey"
                placeholder="Wähle Hauptgericht und Salat-Option"
                variant="solo"
                :items="mainDishItems"
                ref="selectRef"
                multiple
              >
                <template v-slot:selection="{ item }">
                  <v-chip
                    class="ms-2"
                    variant="elevated"
                    :color="decideColor(item.value)"
                  >
                    <span>{{ item.title }}</span>
                  </v-chip>
                </template>
                <template v-slot:item="{ props, item }">
                  <v-divider v-if="item.value === 3"></v-divider>
                  <v-list-item class="h-75" v-bind="props" title="">
                    <div class="d-flex justify-space-between">
                      <v-checkbox-btn
                        :model-value="foodChoice.includes(item.value)"
                        true-icon="mdi-circle"
                        false-icon="mdi-circle"
                        :color="decideColor(item.value)"
                        :label="item.title"
                      ></v-checkbox-btn>
                    </div>
                  </v-list-item>
                </template>
              </v-select>
            </div>
          </v-card>
        </template>

        <template v-slot:next>
          <v-btn
            @click="incrementStep"
            :disabled="step1Valid"
            v-if="stepperValue === 1"
            variant="tonal"
            >Weiter</v-btn
          >
          <v-btn
            @click="incrementStep"
            :disabled="step2Valid"
            v-if="stepperValue === 2"
            variant="tonal"
            >Weiter</v-btn
          >
          <v-btn
            @click="finish"
            :disabled="step3Valid"
            v-if="stepperValue === 3"
            variant="tonal"
            >Bestellung aufgeben</v-btn
          >
        </template>
      </v-stepper>
      <!-- </v-card-text> -->
      <!-- </v-card> -->
    </div>
  </v-dialog>
</template>

<script setup>
import axios from "axios";

const dialog = ref(false);
const stepperValue = ref();
const dateSelection = ref();
const locationItems = ref([]);
const locationSelection = ref();
const step1Valid = ref(true);
const step2Valid = ref(true);
const step3Valid = ref(true);
const foodChoice = ref([]);
const selectRef = useTemplateRef("selectRef");

const checkForOneMainDish = () => {
  if (foodChoice.value.includes(1) && foodChoice.value.includes(2)) {
    foodChoice.value.splice(
      Math.min(foodChoice.value.indexOf(1), foodChoice.value.indexOf(2)),
      1
    );
  }
  if (foodChoice.value.length === 2) {
    selectRef.value.blur();
  }
  if (foodChoice.value.length > 0) {
    step3Valid.value = false;
  } else {
    step3Valid.value = true;
  }
};

const mainDishItems = [
  {
    title: "Hauptgericht 1",
    value: 1,
  },
  {
    title: "Hauptgericht 2",
    value: 2,
  },
  {
    title: "Salat-Option",
    value: 3,
  },
];

const preOrderObject = {};

const props = defineProps(["personId"]);
console.log(props.personId);

// get all locations for Step 2
axios
  .get(import.meta.env.VITE_API + "/api/locations", { withCredentials: true })
  .then((response) => {
    response.data.forEach((locationobject) =>
      locationItems.value.push({
        title: locationobject.location_name,
        value: locationobject.id,
      })
    );
    console.log(locationItems.value);
  })
  .catch((err) => console.log(err));

const incrementStep = () => {
  stepperValue.value += 1;
};

const decideColor = (itemValue) => {
  if (itemValue === 1) {
    return "primary";
  } else if (itemValue === 2) {
    return "red";
  } else {
    return "success";
  }
};

const finish = () => {
  addDateToPreOrderObject();
  addLocationToPreOrderObject();
  addDishesToPreOrderObject();
  preOrderObject.person_id = props.personId;
  console.log(preOrderObject);
  axios
    .post(import.meta.env.VITE_API + "/api/pre-orders/users", preOrderObject, {
      withCredentials: true,
    })
    .then((response) => {
      console.log(response.data);
      dialog.value = false;
    })
    .catch((err) => {
      console.log(err);
    });
};

const addDateToPreOrderObject = () => {
  if (dateSelection.value != undefined) {
    const clickedDate = new Date(dateSelection.value);
    clickedDate.setHours(1);
    preOrderObject.date = clickedDate.toISOString().split("T")[0];
    console.log(preOrderObject);
  }
};
const addLocationToPreOrderObject = () => {
  if (locationSelection.value != undefined) {
    preOrderObject.location_id = locationSelection.value;
    console.log(preOrderObject);
  }
};

const addDishesToPreOrderObject = () => {
  preOrderObject.nothing = false;
  if (foodChoice.value.includes(3)) {
    preOrderObject.salad_option = true;
  } else {
    preOrderObject.salad_option = false;
  }
  if (foodChoice.value.includes(1)) {
    preOrderObject.main_dish = "blau";
  } else {
    preOrderObject.main_dish = "rot";
  }
};
</script>
<style scoped>
.test {
  color: #607d8b !important;
}
</style>

<style>
.v-stepper-item__avatar.v-avatar {
  background: #1867c0 !important;
}
.zUp {
  position: absolute;
  z-index: 1000 !important;
}
</style>

<!-- Dummy -->
