<template>
  <NavbarVerwaltung />
  <v-container
    maxHeight="90%"
    class="pa-0 w-lg-100 d-flex align-center justify-center h-100"
  >
    <div>
      <v-card
        :min-Width="lgAndUp ? 900 : 500"
        :minHeight="lgAndUp ? '100%' : '40vh'"
        class="elevation-1 mt-n3 px-10 w-100 w-lg-100 bg-blue-grey-lighten-5"
      >
        <v-form ref="validation" v-model="form" @submit.prevent="handleSubmit">
          <v-container class="pa-0">
            <div>
              <v-card-text
                class="mt-2 px-0 mb-5 text-h6 text-blue-grey text-start"
              >
                <v-icon class="me-2">mdi-account</v-icon> Neues Benutzerkonto
                anlegen
              </v-card-text>
              <v-radio-group
                v-model="user_group"
                :rules="[required]"
                color="primary"
              >
                <div
                  class="w-100 bg-white text-blue-grey d-lg-flex elevation-1 rounded py-3 px-1"
                >
                  <div class="d-flex w-100 align-center">
                    <v-radio label="Verwaltung" value="verwaltung"></v-radio>
                    <v-radio
                      label="Standortleitung"
                      value="standortleitung"
                    ></v-radio>
                  </div>
                  <div class="d-flex w-100 justify-space-between">
                    <v-radio
                      label="Gruppenleitung"
                      value="gruppenleitung"
                    ></v-radio>
                    <v-radio
                      label="Küchenpersonal"
                      value="kuechenpersonal"
                    ></v-radio>
                  </div>
                </div>
              </v-radio-group>
            </div>
            <div class="d-lg-flex ga-lg-10">
              <div class="w-100 h-100">
                <v-text-field
                  placeholder="Vorname"
                  variant="solo"
                  v-model="first_name"
                  :rules="[required]"
                  base-color="blue-grey"
                  color="blue-grey"
                  class="custom-label-color"
                  label="Vorname"
                  clearable
                ></v-text-field>
              </div>
              <div class="w-100">
                <v-text-field
                  placeholder="Nachname"
                  variant="solo"
                  base-color="blue-grey"
                  color="blue-grey"
                  v-model="last_name"
                  :rules="[required]"
                  class="mb-2 custom-label-color"
                  label="Nachname"
                  clearable
                ></v-text-field>
              </div>
            </div>
            <div class="d-lg-flex h-100 ga-lg-10 mt-n2 mb-5">
              <div class="w-100">
                <v-text-field
                  placeholder="Benutzername"
                  base-color="blue-grey"
                  color="blue-grey"
                  variant="solo"
                  v-model="username"
                  :rules="[required]"
                  class="mb-10 custom-label-color"
                  label="Benutzername"
                  clearable
                ></v-text-field>
              </div>

              <CustomAlert
                v-if="notSuccessful"
                class="mb-7"
                :text="errorMessage"
                color="red"
                icon="$error"
              />
              <div class="w-100">
                <v-btn
                  class="py-7"
                  :disabled="!form"
                  color="primary"
                  size="large"
                  type="submit"
                  variant="elevated"
                  block
                >
                  anlegen
                </v-btn>
              </div>
            </div>
          </v-container>
        </v-form>
      </v-card>
    </div>
  </v-container>
  <ConfirmDialogCreateUser
    v-if="showConfirm"
    :showConfirm="showConfirm"
    :userName="username"
    :userGroup="user_group"
    text="Das Benutzerkonto wurde erfolgreich angelegt"
    :initialPassword="initialPassword"
    @close="emptyForm"
  />
</template>

<script setup>
import ConfirmDialogCreateUser from "@/components/ConfirmDialogCreateUser.vue";
import CustomAlert from "@/components/CustomAlert.vue";
import axios from "axios";

import { onMounted } from "vue";
import { useDisplay } from "vuetify";

const { mdAndUp, lgAndUp } = useDisplay();

const validation = ref("");
const showConfirm = ref(false);
const form = ref(false);
const first_name = ref("");
const last_name = ref("");
const username = ref("");
const user_group = ref("");
const user_location = ref();
const allLocations = ref([]);
const notSuccessful = ref(false);
const errorMessage = ref();
const initialPassword = ref("");

const handleSubmit = () => {
  axios
    .post(
      import.meta.env.VITE_API + "/api/users ",
      {
        first_name: first_name.value,
        last_name: last_name.value,
        user_group: user_group.value,
        username: username.value,
      },
      { withCredentials: true }
    )
    .then((response) => {
      console.log(response.data.id);
      axios
        .put(
          `${import.meta.env.VITE_API}/api/users/${
            response.data.id
          }/reset-password`,
          {},
          { withCredentials: true }
        )
        .then((response) => {
          initialPassword.value = response.data.new_password;
          showConfirm.value = true;
        })
        .catch((err) => {
          notSuccessful.value = true;
          console.log(err);
          errorMessage.value = err.response.data.description;
        });
    })
    .catch((err) => {
      notSuccessful.value = true;
      console.log(err);
      errorMessage.value = err.response.data.description;
    });
};

const required = (v) => {
  return !!v || "Eingabe erforderlich";
};

const emptyForm = () => {
  showConfirm.value = false;
  validation.value.reset();
};
</script>

<style scoped>
.custom-label-color >>> .v-label {
  color: #607d8b;
}
.custom-placeholder-color >>> input,
.custom-label-color >>> input {
  color: #607d8b !important;
}
</style>
