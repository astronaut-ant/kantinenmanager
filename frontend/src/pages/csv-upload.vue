<template>
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
  </v-container>
</template>
  
             
  <script setup>
  import axios from "axios";
  const formdata = new FormData()
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
    if (fileError.value) return;
    loading.value = true;
    formdata.append()
    axios.post("DUMMY",{body:{data:formdata}})
  };
  </script>