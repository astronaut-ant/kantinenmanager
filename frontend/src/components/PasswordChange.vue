<template>
  <v-dialog
    color=""
    v-model="dialog"
    max-width="600"
    :persistent="true"
    :no-click-animation="true"
  >
    <template v-slot:activator="{ props: activatorProps }">
      <v-btn variant="text" v-bind="activatorProps" class="text-blue-grey"
        ><v-icon class="me-4">mdi-key-variant</v-icon>Passwort ändern</v-btn
      >
    </template>

    <v-card color="blue-grey-lighten-5">
      <v-form
        ref="validation"
        v-model="form"
        validate-on="lazy invalid-input"
        @submit.prevent="handleSubmit"
      >
        <v-card-text class="mx-auto w-75">
          <h2 class="mt-8 mb-8 text-blue-grey font-weight-bold">
            <v-icon class="me-4 text-blue-grey">mdi-key-variant</v-icon>Passwort
            ändern
          </h2>
          <CustomAlert
            class="mb-6"
            v-if="showAlert"
            :color="alertColor"
            :icon="alertIcon"
            :text="alertText"
          />
          <v-text-field
            base-color="blue-grey"
            color="blue-grey"
            variant="solo"
            :append-inner-icon="
              showOldPassword ? 'mdi-eye-off-outline' : 'mdi-eye-outline'
            "
            class="mt-3"
            label="Altes Passwort*"
            :type="showOldPassword ? 'text' : 'password'"
            v-model="passwordOld"
            :rules="[required]"
            @click:append-inner="showOldPassword = !showOldPassword"
            required
          ></v-text-field>
          <v-text-field
            base-color="blue-grey"
            color="blue-grey"
            variant="solo"
            :append-inner-icon="
              showNewPassword ? 'mdi-eye-off-outline' : 'mdi-eye-outline'
            "
            class="mt-3"
            label="Neues Passwort*"
            :type="showNewPassword ? 'text' : 'password'"
            v-model="passwordNew"
            :rules="[required, minlength]"
            @click:append-inner="showNewPassword = !showNewPassword"
            required
          ></v-text-field>
          <v-text-field
            base-color="blue-grey"
            color="blue-grey"
            variant="solo"
            :append-inner-icon="
              showConfirmPassword ? 'mdi-eye-off-outline' : 'mdi-eye-outline'
            "
            class="mt-3"
            label="Neues Passwort bestätigen*"
            :type="showConfirmPassword ? 'text' : 'password'"
            v-model="passwordConf"
            :rules="[required, minlength]"
            validate-on="input"
            @click:append-inner="showConfirmPassword = !showConfirmPassword"
            required
          ></v-text-field>
          <small class="text-caption text-medium-emphasis text-end"
            >* Pflichtfeld</small
          >
        </v-card-text>
        <v-divider></v-divider>

        <v-card-actions class="mx-auto w-75 pa-3">
          <v-spacer></v-spacer>
          <v-btn :text="goBackText" variant="plain" @click="close"></v-btn>
          <v-btn
            v-if="isFilling"
            type="submit"
            class="bg-primary"
            text="Speichern"
            variant="elevated"
            :disabled="!form"
          ></v-btn>
        </v-card-actions>
      </v-form>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { useAppStore } from "@/stores/app";
import CustomAlert from "./CustomAlert.vue";
import axios from "axios";
const appStore = useAppStore();
const dialog = ref(false);
const passwordOld = ref("");
const passwordNew = ref("");
const passwordConf = ref("");
const form = ref(false);
const showAlert = ref(false);
const alertText = ref("");
const alertColor = ref("");
const alertIcon = ref("");
const validation = ref("");
const goBackText = ref("abbrechen");
const isFilling = ref(true);
const showOldPassword = ref(false);
const showNewPassword = ref(false);
const showConfirmPassword = ref(false);

const required = (v) => {
  return !!v || "Eingabe erforderlich";
};
const minlength = (v) => {
  if (v.length >= 8) {
    return true;
  } else {
    return "Mindestlänge 8 Zeichen";
  }
};
const handleSubmit = () => {
  if (passwordNew.value != passwordConf.value) {
    alertText.value = "Passwortbestätigung fehlgeschlagen";
    alertColor.value = "red";
    alertIcon.value = "$error";
    showAlert.value = true;
  } else {
    axios
      .post(
        "http://localhost:4200/api/account/change-password",
        {
          new_password: passwordNew.value,
          old_password: passwordOld.value,
        },
        { withCredentials: true }
      )
      .then((response) => {
        console.log(response.data.id);
        alertText.value = "Passwort geändert";
        alertColor.value = "success";
        alertIcon.value = "$success";
        showAlert.value = true;
        goBackText.value = "zurück";
        isFilling.value = false;
      })
      .catch((err) => {
        alertText.value = "Altes Passwort falsch";
        alertColor.value = "red";
        alertIcon.value = "$error";
        showAlert.value = true;
      });
  }
};

const close = () => {
  dialog.value = false;
  goBackText.value = "abbrechen";
  validation.value.reset();
  showAlert.value = false;
  isFilling.value = true;
};
</script>
