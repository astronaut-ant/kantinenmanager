<template>
  <NavbarVerwaltung />
  <div class="mt-10 d-flex justify-center">
    <div>
      <v-card class="elevation-7 px-6 py-4 w-100">
        <v-card-text class="mb-2 text-h5">
          Neues Benutzerkonto anlegen
        </v-card-text>
        <v-form ref="validation" v-model="form" @submit.prevent="handleSubmit">
          <v-radio-group
            v-model="user_group"
            :rules="[required]"
            color="primary"
          >
            <div>
              <v-radio label="Verwaltung" value="verwaltung"></v-radio>
              <v-radio
                label="Standortleitung"
                value="standortleitung"
              ></v-radio>
              <v-radio label="Gruppenleitung" value="gruppenleitung"></v-radio>
              <v-radio label="Küchenpersonal" value="kuechenpersonal"></v-radio>
            </div>
          </v-radio-group>
          <v-text-field
            v-model="username"
            :rules="[required]"
            class="mb-2"
            label="Benutzername"
            clearable
          ></v-text-field>
          <v-text-field
            v-model="password"
            type="password"
            :rules="[required]"
            label="Passwort"
            clearable
          ></v-text-field>
          <v-btn
            class="mt-5"
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
import router from "../router";
const validation = ref("");
const showConfirm = ref(false);
const form = ref(false);
const username = ref("");
const password = ref("");
const user_group = ref("");

const handleSubmit = () => {
  axios
    .post("http://localhost:4200/api/users ", {
      username: username.value,
      password: password.value,
      user_group: user_group.value,
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

watch([username, password, user_group], emptyForm);
</script>
