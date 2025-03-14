<template>
  <NavbarVerwaltung
    :breadcrumbs="[{ title: 'Mitarbeiter' }, { title: 'Neuer Mitarbeiter' }]"
  />
  <div class="d-flex justify-center mt-14">
    <v-card width="500" class="px-10 py-2 mt-10">
      <div class="d-flex justify-start">
        <h1 class="text-primary">
          <v-icon class="me-2">mdi-database-import</v-icon>Import CSV Dateien
        </h1>
      </div>

      <div class="d-flex justify-center mt-10">
        <div class="flex-grow-1" style="max-width: 600px; width: 100%">
          <v-form>
            <v-file-input
              :active="true"
              base-color="blue-grey"
              color="primary"
              variant="outlined"
              Placeholder="Wähle eine Datei aus"
              v-model="file"
              label="Upload"
              accept=".csv"
              outlined
              :error-messages="fileError"
              :disabled="loading"
              @change="onFileChange"
            ></v-file-input>
            <v-card-actions class="justify-end mt-2 me-n2">
              <v-btn
                :disabled="loading"
                variant="text"
                to="/verwaltung/mitarbeiter/neuerMitarbeiter"
                color="blue-grey"
              >
                Zurück
              </v-btn>
              <v-btn
                class="bg-primary"
                :disabled="!file || fileError || loading"
                :loading="loading"
                @click="uploadFile"
              >
                Hochladen
              </v-btn></v-card-actions
            >
          </v-form>
        </div>
      </div>
      <!--
      <div class="d-flex justify-center mt-5">
        <div style="max-width: 600px; width: 100%">
          <v-divider></v-divider>
        </div>
      </div>

      <div class="d-flex justify-center mt-4"></div> -->

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
    </v-card>
  </div>
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
