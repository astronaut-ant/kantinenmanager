<template>
  <NavbarVerwaltung :breadcrumbs = '[{"title": "Mitarbeiter"}, {"title": "Neuer Mitarbeiter"}]'/>
  <v-container class="py-5">
    <div class="d-flex justify-center">
      <h1 class="text-center">Import CSV Dateien</h1>
    </div>

    <div class="d-flex justify-center mt-5">
      <div class="flex-grow-1" style="max-width: 600px; width: 100%">
        <v-form>
          <v-file-input
            v-model="file"
            label="Wähle eine Datei aus"
            accept=".csv"
            outlined
            :error-messages="fileError"
            :disabled="loading"
            @change="onFileChange"
          ></v-file-input>
          <v-btn
            block
            class="bg-primary"
            :disabled="!file || fileError || loading"
            :loading="loading"
            @click="uploadFile"
          >
            Hochladen
          </v-btn>
        </v-form>
      </div>
    </div>

    <div class="d-flex justify-center mt-5">
      <div style="max-width: 600px; width: 100%">
        <v-divider></v-divider>
      </div>
    </div>

    <div class="d-flex justify-center mt-4">
      <v-btn
        :disabled="loading"
        to="/verwaltung/mitarbeiter/neuerMitarbeiter"
        class="bg-red"
      >
        Zurück
      </v-btn>
    </div>

    <SuccessSnackbar
      v-model="successSnackbar"
      :text="snackbarText"
    ></SuccessSnackbar>

    <v-dialog v-model="errorDialog" persistent max-width="400">
      <v-card>
        <v-card-title class="text-error d-flex justify-start">
          <v-icon left class="mr-2"> mdi-alert-circle-outline </v-icon>
          <span class="text-h5">Fehler</span>
        </v-card-title>
        <v-card-text
          >Fehler beim Hochladen der Datei. Bitte versuchen Sie es
          erneut.</v-card-text
        >
        <v-card-actions>
          <v-btn color="error" text @click="closeErrorDialog">OK</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import axios from "axios";
const file = ref(null);
const fileError = ref(null);
const loading = ref(false);
const successSnackbar = ref(false);
const snackbarText = ref("Die Datei wurde erfolgreich hochgeladen!");
const errorDialog = ref(false);

const onFileChange = () => {
  if (!file.value) {
    fileError.value = null;
    return;
  }
  if (!file.value.name.endsWith(".csv")) {
    fileError.value = "Nur CSV Dateien sind erlaubt!";
    file.value = null;
  } else {
    fileError.value = null;
  }
};

const uploadFile = () => {
  if (fileError.value || !file.value) return;
  loading.value = true;

  const formData = new FormData();
  formData.append("file", file.value);

  axios
    .post(import.meta.env.VITE_API + "/api/employees_csv", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
      withCredentials: true,
    })
    .then((response) => {
      console.log(response.data);
      successSnackbar.value = true;
    })
    .catch((err) => {
      console.error(err);
      errorDialog.value = true;
    })
    .finally(() => {
      loading.value = false;
      file.value = null;
    });
};

const closeErrorDialog = () => {
  errorDialog.value = false;
};
</script>
