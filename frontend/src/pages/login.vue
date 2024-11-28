<template>
  <v-dialog
    v-model="dialog"
    :persistent="true"
    :no-click-animation="true"
    max-width="600"
  >
    <v-card class="mx-auto px-6 py-4" min-width="344">
      <v-card-text class="text-center text-h5">
        SIGN IN
        <v-icon>mdi-login</v-icon>
      </v-card-text>
      <v-form v-model="form" @submit.prevent="handleSubmit">
        <v-text-field
          v-model="userName"
          :readonly="loading"
          :rules="[required]"
          class="mb-2"
          label="Benutzername"
          clearable
        ></v-text-field>
        <v-text-field
          v-model="password"
          type="password"
          :readonly="loading"
          :rules="[required]"
          label="Passwort"
          clearable
        ></v-text-field>
        <v-btn
          class="mt-5"
          :disabled="!form"
          :loading="loading"
          color="primary"
          size="large"
          type="submit"
          variant="elevated"
          block
        >
          Sign In
        </v-btn>
        <LoginAlert v-if="showAlert" />
      </v-form>
    </v-card>
  </v-dialog>
</template>

<script setup>
import axios from "axios";
import router from "../router";
import { useAppStore } from "../stores/app.js";
import LoginAlert from "@/components/LoginAlert.vue";

const form = ref(false);
const userName = ref(null);
const password = ref(null);
const loading = ref(false);
const dialog = ref(true);
const showAlert = ref(false);

const handleSubmit = async () => {
  const appStore = useAppStore();
  if (!form) return;
  await axios
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
      console.log(appStore.userData);
    })
    .catch((err) => console.log(err));
  // loading.value = true;
  // setTimeout(() => (loading.value = false), 2000);

  switch (appStore.userData.user_group) {
    case "verwaltung":
      router.push({ path: "/verwaltung/uebersicht" });
      break;
    case "standortleitung":
      router.push({ path: "/standortleitung/uebersicht" });
      break;
    case "gruppenleitung":
      router.push({ path: "/gruppenleitung" });
      break;
    case "kuechenpersonal":
      router.push({ path: "/kuechenpersonal/uebersicht" });
      break;
    default:
      showAlert.value = true;
  }
};

const required = (v) => {
  return !!v || "Eingabe erforderlich";
};
</script>
