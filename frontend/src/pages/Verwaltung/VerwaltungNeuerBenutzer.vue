<template>
  <NavbarVerwaltung
    :breadcrumbs="[{ title: 'Benutzer' }, { title: 'Neuer Benutzer' }]"
  />

  <div class="d-flex justify-center pa-15">
    <div>
      <v-card
        class="elevation-7 px-8 py-4 w-100 text-blue-grey-darken-3"
        min-width="700"
      >
        <v-card-text class="mb-2 text-h6">
          <div class="d-flex ga-4 mt-n3 ms-2 ms-n4 text-primary">
            <div class="d-flex align-center mt-n2">
              <v-icon :size="40">mdi-account-plus</v-icon>
            </div>
            <h2>Neues Benutzerkonto anlegen</h2>
          </div>
        </v-card-text>
        <v-form ref="validation" v-model="form" @submit.prevent="handleSubmit">
          <v-radio-group
            v-model="user_group"
            :rules="[required]"
            color="primary"
          >
            <div class="d-flex">
              <v-radio
                base-color="blue-grey"
                class="ms-n2"
                label="Verwaltung"
                value="verwaltung"
              >
                <template v-slot:label="{ label }">
                  <span class="text-blue-grey-darken-4">{{ label }} </span>
                </template></v-radio
              >
              <v-radio
                base-color="blue-grey"
                label="Standortleitung"
                value="standortleitung"
              >
                <template v-slot:label="{ label }">
                  <span class="text-blue-grey-darken-4">{{ label }} </span>
                </template>
              </v-radio>
            </div>
            <div class="d-flex">
              <v-radio
                base-color="blue-grey"
                class="ms-n2"
                label="Gruppenleitung"
                value="gruppenleitung"
              >
                <template v-slot:label="{ label }">
                  <span class="text-blue-grey-darken-4">{{ label }} </span>
                </template></v-radio
              >
              <v-radio
                base-color="blue-grey"
                label="Küchenpersonal"
                value="kuechenpersonal"
              >
                <template v-slot:label="{ label }">
                  <span class="text-blue-grey-darken-4">{{ label }} </span>
                </template></v-radio
              >
            </div>
          </v-radio-group>
          <div class="d-flex ga-5 mt-2 mb-2">
            <v-text-field
              :active="true"
              v-model="first_name"
              :rules="[required]"
              @update:model-value="hasChanged = true"
              base-color="blue-grey"
              color="primary"
              variant="outlined"
              class="mb-2 w-100"
              label="Vorname"
              placeholder="Vornamen eingeben"
              clearable
            ></v-text-field>
            <v-text-field
              :active="true"
              v-model="last_name"
              @update:model-value="hasChanged = true"
              base-color="blue-grey"
              color="primary"
              variant="outlined"
              :rules="[required]"
              class="mb-2 w-100"
              label="Nachname"
              placeholder="Nachnamen eingeben"
              clearable
            ></v-text-field>
          </div>
          <div block>
            <v-text-field
              :active="true"
              base-color="blue-grey"
              @update:model-value="hasChanged = true"
              color="primary"
              variant="outlined"
              class="mb-5 mt-2"
              v-model="username"
              :rules="[required]"
              label="Benutzername"
              placeholder="Eindeutigen Benutzernamen vergeben"
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
          <v-card-actions class="justify-end me-n2">
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
