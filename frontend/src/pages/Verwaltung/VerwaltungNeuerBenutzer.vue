<template>
  <NavbarVerwaltung />

  <div class="d-flex justify-center mt-7">
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
          <v-select
            v-if="user_group === 'kuechenpersonal'"
            v-model="user_location"
            :items="allLocations"
            :rules="[required]"
            label="Standort"
          ></v-select>
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
            class="mb-2"
            label="Benutzername"
            clearable
          ></v-text-field>
          <CustomAlert
            v-if="notSuccessful"
            class="mb-7"
            :text="errorMessage"
            color="red"
            icon="$error"
          />
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
      </v-card>
    </div>
  </div>
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
    .post("http://localhost:4200/api/users ", {
      first_name: first_name.value,
      last_name: last_name.value,
      password: "12345678",
      user_group: user_group.value,
      username: username.value,
    })
    .then((response) => {
      console.log(response.data.id);
      axios
        .put(
          `http://localhost:4200/api/users/${response.data.id}/reset-password`,
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
onMounted(() => {
  axios
    .get("http://localhost:4200/api/locations", { withCredentials: true })
    .then((response) => {
      response.data.forEach((location) => {
        allLocations.value.push(location.location_name);
      });
      console.log(allLocations.value);
    })
    .catch((err) => console.log(err.response.data.description));
});
</script>
