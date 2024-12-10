<template>
  <v-container class="d-flex h-100 align-center">
    <v-card class="mx-auto px-6 py-4 w-50 bg-blue-grey-lighten-5">
      <v-card-text
        class="text-center text-h5 underlined text-blue-grey font-weight-bold mb-2"
      >
        LOGIN
      </v-card-text>

      <v-form v-model="form" @submit.prevent="handleSubmit">
        <v-text-field
          v-model="userName"
          base-color="blue-grey"
          color="blue-grey"
          variant="solo"
          :readonly="loading"
          :rules="[required]"
          class="mb-2"
          label="Benutzername"
          clearable
        ></v-text-field>
        <v-text-field
          v-model="password"
          base-color="blue-grey"
          color="blue-grey"
          variant="solo"
          type="password"
          :readonly="loading"
          :rules="[required]"
          label="Passwort"
          clearable
        ></v-text-field>
        <CustomAlert
          class="mb-5"
          color="red"
          icon="$error"
          text="Ungültiger Benutzername oder Passwort"
          v-if="showAlert"
        />
        <v-container class="d-flex justify-center">
          <v-btn
            class="mb-2 elevation-2"
            :disabled="!form"
            :loading="loading"
            color="primary"
            size="large"
            type="submit"
            variant="elevated"
          >
            Einloggen <v-icon class="ms-2">mdi-login</v-icon>
          </v-btn>
        </v-container>
      </v-form>
    </v-card>
  </v-container>
</template>

<script setup>
import axios from "axios";
import router from "../router";
import { useAppStore } from "../stores/app.js";
import CustomAlert from "@/components/CustomAlert.vue";

const form = ref(false);
const userName = ref(null);
const password = ref(null);
const loading = ref(false);
const dialog = ref(true);
const showAlert = ref(false);

const required = (v) => {
  return !!v || "Eingabe erforderlich";
};

const handleSubmit = () => {
  const appStore = useAppStore();
  if (!form) return;
  axios
    .post(
      "http://localhost:4200/api/login",
      {
        username: userName.value,
        password: password.value,
      },
      { withCredentials: true }
    )
    .then((response) => {
      appStore.userData = response.data;
      switch (appStore.userData.user_group) {
        case "verwaltung":
          console.log("v");
          router.push({ path: "/verwaltung/benutzer/uebersicht" });
          break;
        case "standortleitung":
          console.log("s");
          router.push({ path: "/standortleitung/uebersicht" });
          break;
        case "gruppenleitung":
          console.log("g");
          router.push({ path: "/gruppenleitung/uebersicht" });
          break;
        case "kuechenpersonal":
          console.log("k");
          router.push({ path: "/kuechenpersonal/uebersicht" });
          break;
      }
    })
    .catch((err) => (showAlert.value = true));
};
</script>
