<template>
  <NavbarVerwaltung @click="emptyForm" />
  <div class="mt-7 d-flex justify-center" @click="emptyForm">
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
            <div class="d-flex">
              <v-radio label="Verwaltung" value="verwaltung"></v-radio>
              <v-radio
                label="Standortleitung"
                value="standortleitung"
              ></v-radio>
            </div>
            <div class="d-flex">
              <v-radio label="Gruppenleitung" value="gruppenleitung"></v-radio>
              <v-radio label="Küchenpersonal" value="kuechenpersonal"></v-radio>
            </div>
          </v-radio-group>
          <v-text-field
            v-model="first_name"
            :rules="[required]"
            class="mb-2"
            label="Vorname"
            clearable
          ></v-text-field>
          <v-text-field
            v-model="last_name"
            :rules="[required]"
            class="mb-2"
            label="Nachname"
            clearable
          ></v-text-field>
          <v-text-field
            v-model="username"
            :rules="[required]"
            label="Benutzername"
            clearable
          ></v-text-field>
          <div class="d-flex justify-center mt-2 mb-5">
            <v-btn size="large" class="w-100 bg-red" @click="generatePassword"
              >Generiere Passwort</v-btn
            >
          </div>
          <v-text-field
            :append-inner-icon="
              showPassword ? 'mdi-eye-off-outline' : 'mdi-eye-outline'
            "
            v-model="password"
            :type="showPassword ? 'text' : 'password'"
            :rules="[required]"
            :readonly="true"
            label="Passwort"
            @click:append-inner="showPassword = !showPassword"
          >
          </v-text-field>

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
const first_name = ref("");
const last_name = ref("");
const username = ref("");
const password = ref("");
const user_group = ref("");
const showPassword = ref(false);

//Dummy => fetch from Backend
const generatePassword = () => {
  password.value = "12345678";
};

const test = () => {
  console.log("test");
};
const handleSubmit = () => {
  axios
    .post("http://localhost:4200/api/users ", {
      first_name: first_name.value,
      last_name: last_name.value,
      username: username.value,
      password: password.value,
      user_group: user_group.value,
    }, { withCredentials: true })
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
</script>
