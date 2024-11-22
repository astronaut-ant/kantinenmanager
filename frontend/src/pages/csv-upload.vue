<template>
  <NavbarVerwaltung />
  <v-container>
    <h1 class="text-center mt-5">Import CSV Dateien</h1>
    <div class="d-flex justify-center">
      <div class="w-50 mt-10">
        <v-row>
          <v-col cols="12">
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
                :disabled="!file || fileError || loading"
                :loading="loading"
                @click="uploadFile"
                class="bg-primary"
              >
                Hochladen
              </v-btn>
            </v-form>
          </v-col>
        </v-row>
      </div>
    </div>
    <v-dialog v-model="successDialog" persistent max-width="400">
      <v-card>
        <v-card-title class="text-success d-flex justify-start">
          <v-icon left class="mr-2">
            mdi-check-circle-outline
          </v-icon>
          <span class="text-h5">Erfolg</span>  
        </v-card-title>
        <v-card-text>Datei wurde erfolgreich hochgeladen!</v-card-text>
        <v-card-actions>
          <v-btn color="success" text @click="closeSuccessDialog">OK</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <v-dialog v-model="errorDialog" persistent max-width="400">
      <v-card>
        <v-card-title class="text-error d-flex justify-start">
          <v-icon left class="mr-2">
            mdi-alert-circle-outline
          </v-icon>
          <span class="text-h5">Fehler</span>  
        </v-card-title>
        <v-card-text>Fehler beim Hochladen der Datei. Bitte versuchen Sie es erneut.</v-card-text>
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
  const successDialog = ref(false);
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
    .post("DUMMY", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    })
    .then((response) => {
      console.log(response.data);
      successDialog.value = true;
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
  const closeSuccessDialog = () => {
  successDialog.value = false;
  };

  const closeErrorDialog = () => {
  errorDialog.value = false;
  };
  </script>