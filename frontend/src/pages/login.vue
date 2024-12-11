<template>
  <v-container class="d-flex h-100 align-center">
    <v-card class="mx-auto px-6 py-4 w-50 bg-blue-grey-lighten-5">
      <div class="d-flex w-100 h-100 align-center justify-center mb-4">
        <div class="">
          <v-img class="" :width="30" cover src="../assets/logo.png"></v-img>
        </div>
        <div class="">
          <v-card-text
            class="text-center text-h5 text-blue-grey font-weight-bold"
          >
            LOGIN
          </v-card-text>
        </div>
      </div>
      <v-form v-model="form" @submit.prevent="handleSubmit">
        <v-text-field
          v-model="userName"
          base-color="blue-grey"
          color="blue-grey"
          variant="solo"
          :rules="[required]"
          class="mb-2"
          label="Benutzername"
        ></v-text-field>
        <v-text-field
          :append-inner-icon="
            showPassword ? 'mdi-eye-off-outline' : 'mdi-eye-outline'
          "
          v-model="password"
          base-color="blue-grey"
          color="blue-grey"
          variant="solo"
          :type="showPassword ? 'text' : 'password'"
          :rules="[required]"
          label="Passwort"
          @click:append-inner="showPassword = !showPassword"
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
            :disabled="!form"
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
const showAlert = ref(false);
const showPassword = ref(false);

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
