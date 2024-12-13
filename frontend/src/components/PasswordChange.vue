<template>
  <v-dialog
    color=""
    v-model="dialog"
    max-width="600"
    :persistent="true"
    :no-click-animation="true"
  >
    <template v-slot:activator="{ props: activatorProps }">
      <v-btn
        @click="resetForm"
        variant="text"
        v-bind="activatorProps"
        class="text-blue-grey"
        ><v-icon class="me-4">mdi-key-variant</v-icon>Passwort ändern</v-btn
      >
    </template>

    <v-card
      :width="form ? '600' : '550'"
      class="mx-auto px-10"
      color="blue-grey-lighten-5"
    >
      <v-form
        v-model="validation"
        @submit.prevent="handleSubmit"
        validate-on="invalid-input"
      >
        <v-card-text>
          <h2 class="mt-5 mb-6 text-blue-grey font-weight-bold">
            <v-icon class="me-4 text-blue-grey">
              {{ form ? "mdi-key-variant" : "mdi-swap-horizontal" }}</v-icon
            >
            {{ form ? "Passwort ändern" : "Passwort erfolgreich geändert" }}
          </h2>
          <div class="d-flex justify-space-between w-100">
            <AnimatedCircle class="" v-if="!form" />
            <div>
              <h3 class="mt-7 text-blue-grey" v-if="!form">
                (Automatische Abmeldung in 60 Sekunden)
              </h3>
            </div>
          </div>
          <div v-if="form">
            <v-text-field
              base-color="blue-grey"
              :error-messages="oldPasswordWrong"
              @keyup="checkToEnableSubmit"
              @update:modelValue="oldPasswordWrong = ''"
              color="blue-grey"
              variant="solo"
              :append-inner-icon="
                showOldPassword ? 'mdi-eye-off-outline' : 'mdi-eye-outline'
              "
              class="mt-3"
              label="Altes Passwort*"
              :type="showOldPassword ? 'text' : 'password'"
              v-model="passwordOld"
              :rules="[required, minlength]"
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
              @update:modelValue="notMatching = ''"
              @keyup="checkToEnableSubmit"
              :error-messages="notMatching"
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
              label="Neues Passwort wiederholen*"
              :error-messages="notMatching"
              @update:modelValue="notMatching = ''"
              @keyup="checkToEnableSubmit"
              :type="showConfirmPassword ? 'text' : 'password'"
              v-model="passwordConf"
              :rules="[required, minlength]"
              @click:append-inner="showConfirmPassword = !showConfirmPassword"
              required
            ></v-text-field>
            <small class="text-caption text-medium-emphasis text-end"
              >* Pflichtfeld</small
            >
          </div>
        </v-card-text>
        <v-divider></v-divider>

        <v-card-actions class="mb-2 mt-2">
          <v-spacer></v-spacer>
          <v-btn text="Abbrechen" variant="plain" @click="close"></v-btn>
          <v-btn
            v-if="form"
            type="submit"
            class="bg-primary"
            text="Speichern"
            variant="elevated"
            :disabled="!submitEnabled"
          ></v-btn>
          <v-btn
            v-if="!form"
            @click="succeeded"
            class="bg-primary"
            text="Jetzt neu einloggen"
            variant="elevated"
          ></v-btn>
        </v-card-actions>
      </v-form>
    </v-card>
  </v-dialog>
</template>

<script setup>
import axios from "axios";
import AnimatedCircle from "./AnimatedCircle.vue";
import { onMounted } from "vue";
const dialog = ref(false);
const passwordOld = ref("");
const passwordNew = ref("");
const passwordConf = ref("");
const validation = ref(false);
const showOldPassword = ref(false);
const showNewPassword = ref(false);
const showConfirmPassword = ref(false);
const oldPasswordWrong = ref("");
const notMatching = ref("");
const submitEnabled = ref(false);
const timer = ref(60);

const checkToEnableSubmit = () => {
  if (
    passwordConf.value.length >= 8 &&
    passwordNew.value.length >= 8 &&
    passwordOld.value.length >= 8
  ) {
    submitEnabled.value = true;
  } else {
    submitEnabled.value = false;
  }
};

const resetForm = () => {
  form.value = true;
};

const required = (v) => {
  return !!v || "Eingabe erforderlich";
};
const minlength = (v) => {
  return v.length >= 8 || "Mindestlänge 8 Zeichen";
};

const handleSubmit = () => {
  if (validation.value) {
    if (passwordConf.value !== passwordNew.value) {
      notMatching.value = "Passwörter stimmen nicht überein";
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
          form.value = false;
          forceLogout();
        })
        .catch((err) => {
          oldPasswordWrong.value = "Altes Passwort falsch";
        });
    }
  }
};
const form = ref(false);

const emit = defineEmits(["succeeded"]);
const succeeded = () => {
  emit("succeeded");
};

const close = () => {
  dialog.value = false;
  passwordOld.value = "";
  passwordNew.value = "";
  passwordConf.value = "";
  passwordOld.value = "";
  passwordNew.value = "";
  passwordConf.value = "";
  showOldPassword.value = "";
  showNewPassword.value = "";
  showConfirmPassword.value = "";
};

const forceLogout = () => {
  setTimeout(() => {
    succeeded();
  }, 60000);
};
</script>
