<template>
  <v-dialog v-model="dialog" width="400">
    <template v-slot:activator="{ props: activatorProps }">
      <v-btn
        @click="reset"
        v-bind="activatorProps"
        class="mt-2 mb-5"
        color="primary"
      >
        <v-icon class="me-2">mdi-plus</v-icon>Neue Vorbestellung aufgeben
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
          <v-card class="test" color="#ECEFF1" flat>
            <v-card-title class="ps-0 ms-3">Gewünschtes Datum</v-card-title>

            <v-container>
              <v-row justify="center">
                <v-date-picker
                  @update:model-value="step1Valid = false"
                  v-model="dateSelection"
                  elevation="2"
                  class="test"
                  height="350"
                  color="primary"
                  :first-day-of-week="1"
                  :allowed-dates="selectableDates"
                  :hide-header="true"
                >
                </v-date-picker>
              </v-row>
            </v-container>
          </v-card>
        </template>

        <template v-slot:item.2>
          <v-card color="#ECEFF1" class="text-blue-grey" flat>
            <v-card-title class="ps-0">Gewünschter Standort</v-card-title>
            <v-select
              @update:model-value="step2Valid = false"
              v-model="locationSelection"
              placeholder="Standort auswählen"
              :items="locationItems"
              color="blue-grey"
              variant="solo"
            >
              <template v-slot:selection="{ item }">
                <span class="text-blue-grey">{{ item.title }}</span>
              </template>

              <template v-slot:item="{ props, item }">
                <v-list-item class="h-75" v-bind="props" title="">
                  <span class="text-blue-grey">{{ item.title }}</span>
                </v-list-item>
              </template>
            </v-select>
          </v-card>
        </template>

        <template v-slot:item.3>
          <v-card class="text-blue-grey" color="#ECEFF1" flat>
            <v-card-title class="ps-0">Gewünschtes Menü</v-card-title>

            <div class="d-flex">
              <v-select
                clearable
                persistent-clear
                v-model="foodChoice"
                @update:model-value="checkForOneMainDish()"
                @update:menu="changeOpenState"
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

                <template v-slot:append-inner="{}">
                  <v-icon v-if="foodChoice.length === 1 && isOpen">
                    mdi-checkbox-marked-circle</v-icon
                  >
                </template>

                <template v-slot:item="{ props, item }">
                  <v-divider v-if="item.value === 3"></v-divider>
                  <v-list-item class="h-75" v-bind="props" title="">
                    <div class="d-flex justify-space-between">
                      <v-checkbox-btn
                        :model-value="foodChoice.includes(item.value)"
                        class="text-blue-grey"
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
            v-if="stepperValue === 3 && !inEditMode"
            variant="tonal"
            >Bestellung aufgeben</v-btn
          >
          <v-btn
            @click="updateOrder(preOrderToEdit)"
            :disabled="step3Valid"
            v-if="stepperValue === 3 && inEditMode"
            variant="tonal"
            >Bestellung aktualisieren</v-btn
          >
        </template>
      </v-stepper>
      <!-- </v-card-text> -->
      <!-- </v-card> -->
    </div>
    <ConfirmUserOrder
      :show-confirm="showConfirmation"
      @close="(showConfirmation = false), (dialog = false)"
    />
  </v-dialog>
</template>

<script setup>
import axios from "axios";
import ConfirmUserOrder from "./ConfirmUserOrder.vue";
import { useTemplateRef } from "vue";

const stepperValue = ref();
const dateSelection = ref();
const locationItems = ref([]);
const locationSelection = ref();
const step1Valid = ref(true);
const step2Valid = ref(true);
const step3Valid = ref(true);
const foodChoice = ref([]);
const selectRef = useTemplateRef("selectRef");
const selectableDates = ref([]);
const isOpen = ref(false);
const showConfirmation = ref(false);
const inEditMode = ref(false);
const preOrderToEdit = ref();

const changeOpenState = () => {
  isOpen.value = !isOpen.value;
  console.log(isOpen.value);
};

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

const props = defineProps(["personId", "locationItems", "openModal"]);
const emit = defineEmits(["ordered"]);
const dialog = ref(false);
dialog.value = false;
watch(
  () => props.openModal,
  (newVal) => {
    dialog.value = true;
    const preOrderId = newVal[1];
    restore(preOrderId);
    preOrderToEdit.value = preOrderId;
  }
);

locationItems.value = props.locationItems;

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
      showConfirmation.value = true;
      emit("ordered");
      console.log(response.data);
    })
    .catch((err) => {
      console.log(err); //TODO --> Display ErrorMessage for TimeExceeded
    });
};

const updateOrder = (preOrderToEdit) => {
  addDateToPreOrderObject();
  addLocationToPreOrderObject();
  addDishesToPreOrderObject();
  preOrderObject.person_id = props.personId;
  console.log("Test2", preOrderObject);

  //actual BackendError
  //TODO --> Display ErrorMessage for TimeExceeded
  // axios
  //   .put(
  //     import.meta.env.VITE_API + `/api/pre-orders/${preOrderToEdit}`,
  //     preOrderObject,
  //     {
  //       withCredentials: true,
  //     }
  //   )
  //   .then((response) => {
  //     showConfirmation.value = true;
  //     emit("ordered");
  //     console.log("Test3", response.data);
  //   })
  //   .catch((err) => {
  //     console.log(err);
  //   });

  //temporal Workaround (with Delete -> Post)
  //TODO --> Display ErrorMessage for TimeExceeded
  axios
    .delete(import.meta.env.VITE_API + `/api/pre-orders/${preOrderToEdit}`, {
      withCredentials: true,
    })
    .then((response) => {
      console.log(response.data);
      axios
        .post(
          import.meta.env.VITE_API + "/api/pre-orders/users",
          preOrderObject,
          {
            withCredentials: true,
          }
        )
        .then((response) => {
          showConfirmation.value = true;
          emit("ordered");
          console.log(response.data);
        })
        .catch((err) => {
          console.log(err);
        });
    })
    .catch((err) => console.log(err));
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
    console.log("TEST", preOrderObject);
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
  } else if (foodChoice.value.includes(2)) {
    preOrderObject.main_dish = "rot";
  } else {
    preOrderObject.main_dish = null;
  }
};

const calcAllowedDates = () => {
  axios
    .get(
      import.meta.env.VITE_API + `/api/pre-orders?person-id=${props.personId}`,
      {
        withCredentials: true,
      }
    )
    .then((response) => {
      const blockedDates = [];
      const allowedDates = [];
      response.data.forEach((data) => {
        blockedDates.push(data.date);
      });
      console.log("blockedDates", blockedDates);

      const actualDate = new Date();
      // actualDate.setDate(actualDate.getDate() + 1);
      const preOrderTimeExceeded = actualDate.getHours() >= 8;
      if (!preOrderTimeExceeded) {
        allowedDates.push(actualDate.toISOString().split("T")[0]);
      }
      for (let i = 1; i < 13; i++) {
        const nextDate = new Date();
        nextDate.setDate(actualDate.getDate() + i);
        const dayOfWeek = nextDate.getDay();
        if (!(dayOfWeek === 6 || dayOfWeek === 0)) {
          const formattedNextDate = nextDate.toISOString().split("T")[0];
          allowedDates.push(formattedNextDate);
        }
      }
      const filteredDates = allowedDates.filter((date) => {
        return !blockedDates.includes(date);
      });
      selectableDates.value = filteredDates;
    })

    .catch((err) => console.log(err));
};

const calcRestoredAllowedDates = (date) => {
  axios
    .get(
      import.meta.env.VITE_API + `/api/pre-orders?person-id=${props.personId}`,
      {
        withCredentials: true,
      }
    )
    .then((response) => {
      const blockedDates = [];
      const allowedDates = [];
      response.data.forEach((data) => {
        blockedDates.push(data.date);
      });
      console.log("blockedDates", blockedDates);

      const actualDate = new Date();
      // actualDate.setDate(actualDate.getDate() + 1);
      const preOrderTimeExceeded = actualDate.getHours() >= 8;
      if (!preOrderTimeExceeded) {
        allowedDates.push(actualDate.toISOString().split("T")[0]);
      }
      for (let i = 1; i < 13; i++) {
        const nextDate = new Date();
        nextDate.setDate(actualDate.getDate() + i);
        const dayOfWeek = nextDate.getDay();
        if (!(dayOfWeek === 6 || dayOfWeek === 0)) {
          const formattedNextDate = nextDate.toISOString().split("T")[0];
          allowedDates.push(formattedNextDate);
        }
      }
      const filteredDates = allowedDates.filter((date) => {
        return !blockedDates.includes(date);
      });
      selectableDates.value = filteredDates;
      selectableDates.value.push(date);
      console.log("selectable Date", selectableDates.value);
      dateSelection.value = new Date(date);
    })

    .catch((err) => console.log(err));
};

const reset = () => {
  inEditMode.value = false;
  showConfirmation.value = false;
  calcAllowedDates();
  step1Valid.value = true;
  step2Valid.value = true;
  step3Valid.value = true;
  stepperValue.value = 1;
  dateSelection.value = undefined;
  locationSelection.value = undefined;
  foodChoice.value = [];
};

const restore = (preOrderId) => {
  inEditMode.value = true;
  axios
    .get(import.meta.env.VITE_API + `/api/pre-orders/${preOrderId}`, {
      withCredentials: true,
    })
    .then((response) => {
      const preOrderObject = response.data;
      console.log(preOrderObject);
      showConfirmation.value = false;
      calcRestoredAllowedDates(preOrderObject.date);
      step1Valid.value = false;
      step2Valid.value = false;
      step3Valid.value = false;
      stepperValue.value = 1;
      dateSelection.value = new Date(preOrderObject.date);
      locationSelection.value = preOrderObject.location_id;
      foodChoice.value = [];
      if (preOrderObject.main_dish == "blau") {
        foodChoice.value.push(1);
      }
      if (preOrderObject.main_dish == "rot") {
        foodChoice.value.push(2);
      }
      if (preOrderObject.salad_option) {
        foodChoice.value.push(3);
      }
    })
    .catch((err) => console.log(err));
};
</script>
<style scoped lang="scss">
.test {
  color: #607d8b !important;
}
</style>

<style>
.v-stepper-item__avatar.v-avatar {
  background: #1867c0 !important;
}
</style>

<!-- Dummy -->
