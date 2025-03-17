<template>
  <NavbarVerwaltung
    :breadcrumbs="[{ title: 'Mitarbeiter' }, { title: 'Neuer Mitarbeiter' }]"
  />
  <div class="mt-7 d-flex justify-center">
    <div>
      <v-card
        :min-width="350"
        class="elevation-0 px-6 py-4 w-100 text-blue-grey-darken-3"
      >
        <v-card-text class="mb-2 text-h6">
          <div class="d-flex ga-4 mt-n3 mb-2 ms-2 ms-n4 text-primary">
            <div class="d-none d-md-flex align-center mt-n2">
              <v-icon :size="35">mdi-human-capacity-increase</v-icon>
            </div>
            <h2>Neuen Mitarbeiter anlegen</h2>
          </div>
        </v-card-text>
        <v-form ref="validation" v-model="form" @submit.prevent="handleSubmit">
          <div class="d-block d-md-flex ga-8">
            <v-menu color="primary" offset-y>
              <template #activator="{ props }">
                <v-text-field
                  :min-width="250"
                  class="w-100 mb-3"
                  :active="true"
                  base-color="blue-grey"
                  color="primary"
                  variant="outlined"
                  Placeholder="Gruppe auswählen"
                  v-bind="props"
                  v-model="group_name"
                  label="Gruppen Name"
                  :rules="[required]"
                  clearable
                  readonly
                  append-inner-icon="mdi-chevron-down"
                ></v-text-field>
              </template>
              <v-list class="w-75 mb-3">
                <v-list-item color="primary" v-for="area in keys">
                  <v-list-item-title
                    class="text-blue-grey-darken-3 cursor-pointer"
                    >{{ area }}</v-list-item-title
                  >
                  <template v-slot:append>
                    <v-icon icon="mdi-menu-right" size="x-small"></v-icon>
                  </template>
                  <v-menu
                    base-color="blue-grey"
                    color="primary"
                    offset-y
                    activator="parent"
                    open-on-click
                    close-on-content-click
                    location="end"
                  >
                    <v-list class="text-blue-grey-darken-3">
                      <v-list-item
                        v-for="group in groupnames[area]"
                        @click="selectOption(group, area)"
                      >
                        <v-list-item-title>{{ group }}</v-list-item-title>
                      </v-list-item>
                    </v-list>
                  </v-menu>
                </v-list-item>
              </v-list>
            </v-menu>
            <v-container class="pa-0">
              <v-number-input
                :min-width="250"
                hide-details="auto"
                precision="0"
                :active="true"
                base-color="blue-grey"
                color="primary"
                control-variant="default"
                inset
                variant="outlined"
                v-model="employee_number"
                :rules="[required, unique]"
                class="w-100 mb-3"
                label="Mitarbeiter-Nr."
                placeholder="Nummer zuweisen"
                :min="0"
                required
                clearable
              ></v-number-input>
            </v-container>
          </div>

          <div class="d-block d-md-flex ga-8 mt-6">
            <v-text-field
              :min-width="250"
              class="w-100 mb-3"
              :active="true"
              base-color="blue-grey"
              color="primary"
              variant="outlined"
              Placeholder="Vornamen eingeben"
              v-model="first_name"
              :rules="[required]"
              label="Vorname"
              clearable
            ></v-text-field>
            <v-text-field
              :min-width="250"
              class="w-100"
              :active="true"
              base-color="blue-grey"
              color="primary"
              variant="outlined"
              Placeholder="Nachnamen eingeben"
              v-model="last_name"
              :rules="[required]"
              label="Nachname"
              clearable
            ></v-text-field>
          </div>

          <v-card-actions class="justify-end me-n2 mt-2">
            <v-btn
              to="/verwaltung/mitarbeiter/neuerMitarbeiter"
              @click="emptyForm"
              color="blue-grey"
              variant="text"
            >
              Zurück
            </v-btn>
            <v-btn
              :disabled="!form"
              color="primary"
              type="submit"
              variant="elevated"
            >
              anlegen
            </v-btn>
          </v-card-actions>
        </v-form>
        <!-- <div
          v-if="showConfirm"
          class="mt-5 d-flex justify-center align-center ga-5"
        >
          <h3>Hinzugefügt!</h3>
          <v-icon color="success" icon="mdi-check-circle-outline" size="32">
          </v-icon>
        </div> -->
      </v-card>
    </div>
  </div>
</template>

<script setup>
import { useFeedbackStore } from "@/stores/feedback";
const feedbackStore = useFeedbackStore();
import axios from "axios";
const validation = ref("");
const showConfirm = ref(false);
const form = ref(false);
const employee_number = ref(null);
const first_name = ref("");
const last_name = ref("");
const group_name = ref("");
const location_name = ref("");
const groupnames = ref({});
const keys = ref([]);
const groupObjects = ref([]);
const location_id = ref(null);
const empNumberArray = ref([]);

onMounted(() => {
  axios
    .get(import.meta.env.VITE_API + "/api/groups/with-locations", {
      withCredentials: true,
    })
    .then((response) => {
      groupnames.value = response.data;
      keys.value = Object.keys(groupnames.value);
      getGroupObjects();
    })
    .catch((err) => {
      console.error(err);
      feedbackStore.setFeedback(
        "error",
        "snackbar",
        err.response?.data?.title,
        err.response?.data?.description
      );
    });
});

axios
  .get(import.meta.env.VITE_API + "/api/employees", {
    withCredentials: true,
  })
  .then((response) => {
    response.data.forEach((emp) => {
      empNumberArray.value.push(emp.employee_number);
    });
    console.log("Emp-Number:", empNumberArray.value);
  })
  .catch((err) => {
    console.error(err);
    feedbackStore.setFeedback(
      "error",
      "snackbar",
      err.response?.data?.title,
      err.response?.data?.description
    );
  });

const getGroupObjects = () => {
  axios
    .get(import.meta.env.VITE_API + "/api/groups", {
      withCredentials: true,
    })
    .then((response) => {
      groupObjects.value = response.data;
      console.log(groupObjects.value);
    })
    .catch((err) => {
      console.error(err);
      feedbackStore.setFeedback(
        "error",
        "snackbar",
        err.response?.data?.title,
        err.response?.data?.description
      );
    });
};

const handleSubmit = () => {
  axios
    .post(
      import.meta.env.VITE_API + "/api/employees ",
      {
        employee_number: employee_number.value,
        first_name: first_name.value,
        group_name: group_name.value,
        last_name: last_name.value,
        location_name: location_name.value,
      },
      { withCredentials: true }
    )
    .then((response) => {
      console.log(response.data);
      getEmployeesData(response.data.id);
      showConfirm.value = true;
      feedbackStore.setFeedback(
        "success",
        "snackbar",
        " ",
        `${first_name.value} ${last_name.value} wurde erfolgreich angelegt!`
      );
      emptyForm();
    })
    .catch((err) => {
      console.error(err);
      feedbackStore.setFeedback(
        "error",
        "snackbar",
        "Fehler beim Anlegen des Mitarbeiters",
        err.response?.data?.description
      );
    });
};

const getEmployeesData = (id) => {
  axios
    .get(import.meta.env.VITE_API + `/api/employees/${id}`, {
      withCredentials: true,
    })
    .then((response) => {
      console.log(response.data);
    })
    .catch((err) => {
      console.error(err);
      feedbackStore.setFeedback(
        "error",
        "snackbar",
        err.response?.data?.title,
        err.response?.data?.description
      );
    });
};

const required = (v) => {
  return !!v || "Eingabe erforderlich";
};

const unique = (v) => {
  return !empNumberArray.value.includes(v) || "Gruppe bereits vergeben";
};
const onlyIntegers = (value) => {
  if (value === "" || Number.isInteger(Number(value))) {
    return true;
  }
  return "Nur ganze Zahlen erlaubt";
};

const emptyForm = () => {
  showConfirm.value = false;
  validation.value.reset();
};

const selectOption = (option, area) => {
  console.log("groupNames: ", groupnames.value);
  location_id.value = groupObjects.value.find((groupObject) => {
    return groupObject.location.location_name === area;
  }).location.id;
  console.log(location_id.value);
  group_name.value = option;
  location_name.value = area;
};
</script>
