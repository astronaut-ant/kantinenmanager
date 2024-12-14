<template>
  <NavbarVerwaltung />
  <v-container max-width="1000">
    <div>
      <v-toolbar color="white" flat dark>
        <p class="text-h5 font-weight-black" >Übersicht Mitarbeiter</p>
        <v-spacer></v-spacer>
        <v-btn icon="mdi-magnify" @click="toggleSearchField"></v-btn>
        <v-btn icon="mdi-reload" @click="fetchData"></v-btn>
      </v-toolbar>
    </div>
    <div class="d-flex justify-center">
      <v-expand-transition>
        <v-text-field
        v-if="isSearchVisible"
        v-model="search"
        density="compact"
        label="Suche"
        prepend-inner-icon="mdi-magnify"
        variant="solo-filled"
        flat
        hide-details
        single-line
        clearable
        rounded
        ></v-text-field>
      </v-expand-transition>
    </div>
    <div>
      <v-data-table :headers="headers"  :items="items" :search="search" :sort-by="sortBy" :loading="loading" item-value="employee_number">
      <template v-slot:[`item.actions`]="{ item }">
        <v-btn icon="mdi-qrcode" class="bg-green mr-2" @click="getQRCode(item)" size="small"></v-btn>
        <v-btn icon="mdi-lead-pencil" class="bg-primary mr-2" @click="openDialog(item)" size="small"></v-btn>
        <v-btn icon="mdi-trash-can-outline" class="bg-red" @click="opendeleteDialog(item)" size="small"></v-btn>
      </template>
      </v-data-table>
    </div>
  </v-container>
  <v-dialog v-model="deleteDialog" persistent max-width="400">
    <v-card>
      <v-card-text>
        <div class="d-flex justify-center text-red mb-4">
          <p class="text-h5 font-weight-black" >Mitarbeiter löschen</p>
        </div>
        <div class="text-medium-emphasis">
          <p> Sind Sie sicher, dass Sie den Mitarbeiter <strong>{{ employeeToDelete }}</strong> löschen möchten?</p>
        </div>
      </v-card-text>
      <v-card-actions>
        <v-btn text @click="closedeleteDialog">Abbrechen</v-btn>
        <v-btn color="red" variant="elevated" @click="confirmDelete">Löschen</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
  <SuccessSnackbar
    v-model="snackbar"
    :text="snackbarText"
  ></SuccessSnackbar>
</template>


<script setup>
  import axios from "axios";
  const search = ref("");
  const loading = ref(true);
  const isSearchVisible = ref(false);
  const deleteDialog = ref(false);
  const employeeToDelete = ref("");
  const employeeToDeleteID = ref("");
  const snackbar = ref(false);
  const snackbarText = ref("");
  const items = ref([]);
  const employees = ref([]);

  const toggleSearchField = () => {
    if (isSearchVisible.value) {
      search.value = "";
    }
    isSearchVisible.value = !isSearchVisible.value;
  };

  const opendeleteDialog = (item) => {
    employeeToDelete.value = item.last_name + ", " + item.first_name;
    employeeToDeleteID.value = item.id;
    deleteDialog.value= true;
  };

  const closedeleteDialog = () => {
    deleteDialog.value = false;
  };

  const confirmDelete = () => {
    axios
      .delete(`${import.meta.env.VITE_API}/api/employees/${employeeToDeleteID.value}`, { withCredentials: true })
      .then(() => {
        items.value = items.value.filter((item) => item.id !== employeeToDeleteID.value);

        snackbar.value = false;
        snackbarText.value = `${employeeToDelete.value} wurde erfolgreich gelöscht!`;
        snackbar.value = true;
        deleteDialog.value = false;
      })
      .catch((err) => {
        console.error(err);
      })
  };

  const getQRCode = (item) => {
  axios
    .get(`${import.meta.env.VITE_API}/api/persons/create-qr/${item.id}`, {
      responseType: "blob",
      withCredentials: true,
    })
    .then((response) => {
      const blob = new Blob([response.data], { type: response.headers["content-type"] });
      const url = window.URL.createObjectURL(blob);

      const link = document.createElement("a");
      link.href = url;

      const contentDisposition = response.headers["content-disposition"];
      let filename = "download";
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename\*?=(['"]?)(.+?)\1(;|$)/i);
        if (filenameMatch) {
          filename = decodeURIComponent(filenameMatch[2]);
        }
      }

      link.download = filename;
      link.click();
      window.URL.revokeObjectURL(url);

      snackbar.value = false;
      snackbarText.value = "Der QR-Code wurde erfolgreich generiert!";
      snackbar.value = true;
    })
    .catch((err) => {
      console.error("Error getting QR Code", err);
    });
  };

  const fetchData = () => {
    loading.value = true;
    axios
    .get("http://localhost:4200/api/employees", { withCredentials: true })
    .then((response) => {
      employees.value = response.data;
      items.value = employees.value.map((employee) => {
        return {
          id: employee.id,
          first_name: employee.first_name,
          last_name: employee.last_name,
          employee_number: employee.employee_number,
          group_id: employee.group.id,
          group_name: employee.group.group_name || "Unbekannt",
          location_id: employee.group.location.id || null,
          location_name: employee.group.location.location_name || "Unbekannt",
        };
      });
      loading.value = false;
    })
    .catch((err) => console.error("Error fetching data", err));
  };

  onMounted(() => {
    fetchData();
  });

  const headers = [
     { title: "Nummer", key: "employee_number"},
     { title: "Nachname", key: "last_name" },
     { title: "Vorname", key: "first_name" },
     { title: "Gruppe", key: "group_name" },
     { title: "Standort", key: "location_name"},
     { title: "", key: "actions", sortable: false },];
  const sortBy = [{ key: 'employee_number', order: 'asc' }]
</script>
