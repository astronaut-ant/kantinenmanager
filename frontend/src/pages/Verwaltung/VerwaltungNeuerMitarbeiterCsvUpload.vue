<template>
  <NavbarVerwaltung
    :breadcrumbs="[{ title: 'Mitarbeiter' }, { title: 'Neuer Mitarbeiter' }]"
  />
  <div class="d-flex justify-center mt-14">
    <v-card elevation="0" class="py-2 mt-10">
      <div class="d-flex justify-start">
        <h1 class="text-primary ms-1">
          <v-icon class="d-none d-md-inline me-2">mdi-database-import</v-icon
          >Import CSV Dateien
        </h1>
      </div>

      <div class="d-flex justify-center flex-grow-1 mt-10">
        <div>
          <v-form>
            <v-file-input
              :min-width="350"
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
    </v-card>
  </div>
</template>

<script setup>
import { useFeedbackStore } from "@/stores/feedback";
const feedbackStore = useFeedbackStore();
import axios from "axios";
const file = ref(null);
const fileError = ref(null);
const loading = ref(false);

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
      feedbackStore.setFeedback(
        "success",
        "snackbar",
        "",
        "Die Datei wurde erfolgreich hochgeladen!"
      );
    })
    .catch((err) => {
      console.error(err);
      feedbackStore.setFeedback(
        "error",
        "dialog",
        err.response?.data?.title,
        err.response?.data?.description
      );
    })
    .finally(() => {
      loading.value = false;
      file.value = null;
    });
};
</script>
