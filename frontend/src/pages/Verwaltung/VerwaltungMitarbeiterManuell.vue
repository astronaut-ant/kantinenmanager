<template>
  <NavbarVerwaltung
    :breadcrumbs="[{ title: 'Mitarbeiter' }, { title: 'Neuer Mitarbeiter' }]"
  />
  <div class="mt-14 d-flex justify-center">
    <div>
      <v-card
        :min-width="600"
        class="elevation-7 px-6 py-4 w-100 text-blue-grey-darken-3"
      >
        <v-card-text class="mb-2 text-h6">
          <div class="d-flex ga-4 mt-n3 mb-2 ms-2 ms-n4 text-primary">
            <div class="d-flex align-center mt-n2">
              <v-icon :size="35">mdi-human-capacity-increase</v-icon>
            </div>
            <h2>Neuen Mitarbeiter anlegen</h2>
          </div>
        </v-card-text>
        <v-form ref="validation" v-model="form" @submit.prevent="handleSubmit">
          <div class="d-flex ga-8">
            <v-menu color="primary" offset-y>
              <template #activator="{ props }">
                <v-text-field
                  class="w-100"
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
              <v-list>
                <v-list-item color="primary" v-for="area in keys">
                  <v-list-item-title class="text-blue-grey-darken-3">{{
                    area
                  }}</v-list-item-title>
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
                class="w-100"
                label="Mitarbeiter-Nr."
                placeholder="Nummer zuweisen"
                :min="1"
                required
                clearable
              ></v-number-input>
            </v-container>
          </div>

          <div class="d-flex ga-8 mt-6">
            <v-text-field
              class="w-100"
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
            <v-btn @click="emptyForm" color="blue-grey" variant="text">
              Verwerfen
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
  <ErrorSnackbar
    v-model="errorSnackbar"
    :text="errorSnackbarText"
    @close="errorSnackbar = false"
  ></ErrorSnackbar>
</template>

<script setup>
import axios from "axios";
const validation = ref("");
const showConfirm = ref(false);
const form = ref(false);
const employee_number = ref("");
const first_name = ref("");
const last_name = ref("");
const group_name = ref("");
const location_name = ref("");
const groupnames = ref({});
const keys = ref([]);
const errorSnackbar = ref(false);
const errorSnackbarText = ref("");

onMounted(() => {
  axios
    .get(import.meta.env.VITE_API + "/api/groups/with-locations", {
      withCredentials: true,
    })
    .then((response) => {
      groupnames.value = response.data;
      keys.value = Object.keys(groupnames.value);
    })
    .catch((err) => console.log(err));
});

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
      showConfirm.value = true;
    })
    .catch((err) => {
      console.log(err);
      errorSnackbarText.value = "Fehler beim Anlegen des Mitarbeiters!";
      errorSnackbar.value = true;
    });
};

const required = (v) => {
  return !!v || "Eingabe erforderlich";
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
  group_name.value = option;
  location_name.value = area;
};
</script>
