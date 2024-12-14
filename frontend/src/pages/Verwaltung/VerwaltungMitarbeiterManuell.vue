<template>
  <NavbarVerwaltung @click="emptyForm" />
  <div class="mt-7 d-flex justify-center" @click="emptyForm">
    <div>
      <v-card class="elevation-7 px-6 py-4 w-100">
        <v-card-text class="mb-2 text-h5">
          Neuen Mitarbeiter anlegen
        </v-card-text>
        <v-form ref="validation" v-model="form" @submit.prevent="handleSubmit">
          <v-text-field
            v-model.number="emplyee_number"
            :rules="[required]"
            label="Kunden-Nr."
            clearable
          ></v-text-field>
          <v-text-field
            v-model="first_name"
            :rules="[required]"
            label="Vorname"
            clearable
          ></v-text-field>
          <v-text-field
            v-model="last_name"
            :rules="[required]"
            label="Nachname"
            clearable
          ></v-text-field>
          <v-menu offset-y>
            <template #activator="{ props }">
              <v-text-field
                v-bind="props"
                v-model="group_name"
                label="Gruppen Name"
                clearable
                readonly
                append-inner-icon="mdi-chevron-down"
              ></v-text-field>
            </template>
            <v-list>
              <v-list-item v-for="area in keys">
                <v-list-item-title>{{ area }}</v-list-item-title>
                <template v-slot:append>
                  <v-icon icon="mdi-menu-right" size="x-small"></v-icon>
                </template>
                <v-menu
                  offset-y
                  activator="parent"
                  open-on-click
                  open-on-hover
                  close-on-content-click
                  location="end"
                >
                  <v-list>
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
          <v-btn
            class="mt-2"
            :disabled="!form"
            color="primary"
            size="large"
            type="submit"
            variant="elevated"
            block
          >
            anlegen
          </v-btn>
        </v-form>
        <div
          v-if="showConfirm"
          class="mt-5 d-flex justify-center align-center ga-5"
        >
          <h3>Hinzugefügt!</h3>
          <v-icon color="success" icon="mdi-check-circle-outline" size="32">
          </v-icon>
        </div>
      </v-card>
    </div>
  </div>
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
const groupnames = {
  Zedtlitz: ["Gruppe 1", "Gruppe 2", "Gruppe 3"],
  W1: ["Gruppe 1", "Gruppe 2", "Gruppe 3"],
  W8: ["Gruppe 1", "Gruppe 2", "Gruppe 3"],
  W13: ["Gruppe 1", "Gruppe 2", "Gruppe 3"],
};
const keys = Object.keys(groupnames);

const handleSubmit = () => {
  axios
    .post(import.meta.env.VITE_API + "/api/employees ", {
      employee_number: employee_number.value,
      first_name: first_name.value,
      group_name: group_name.value,
      last_name: last_name.value,
      location_name: location_name.value,
    })
    .then((response) => console.log(response.data))
    .catch((err) => console.log(err));
  showConfirm.value = true;
};

const required = (v) => {
  return !!v || "Eingabe erforderlich";
};

const emptyForm = () => {
  if (showConfirm.value) {
    showConfirm.value = false;
    validation.value.reset();
  }
};

const selectOption = (option, area) => {
  group_name.value = option + " - " + area;
  location_name.value = area;
};
</script>
