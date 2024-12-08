<template>
  <NavbarVerwaltung />
  <v-container max-width="1000">
    <div>
      <v-toolbar color="white" flat dark>
        <p class="text-h5 font-weight-black" >Übersicht Mitarbeiter</p>
        <v-spacer></v-spacer>
        <v-btn icon="mdi-magnify" @click="toggleSearchField"></v-btn>
        <v-btn icon="mdi-reload"></v-btn>
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
      <v-data-table :headers="headers"  :items="items" :search="search">
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
    @close="snackbar = false"
  ></SuccessSnackbar>
</template>
 
 
<script setup>
  import axios from "axios";
  const search = ref("");
  const isSearchVisible = ref(false);
  const deleteDialog = ref(false);
  const employeeToDelete = ref("");
  const snackbar = ref(false);
  const snackbarText = ref("");
  const items = ref([]);
  const groups = ref([]);
  const locations = ref([]);
  const employees = ref([]);

  const toggleSearchField = () => {
    if (isSearchVisible.value) {
      search.value = "";
    }
    isSearchVisible.value = !isSearchVisible.value;
  };

  const opendeleteDialog = (item) => {
    employeeToDelete.value = item.lastname + ", " + item.firstname;
    deleteDialog.value= true;
  };

  const closedeleteDialog = () => {
    deleteDialog.value = false;
  };

  const getQRCode = (item) => {
  axios
    .get(`http://localhost:4200/api/persons/create-qr/${item.id}`, {
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

      snackbarText.value = "Der QR-Code wurde erfolgreich generiert!";
      snackbar.value = true;
    })
    .catch((err) => {
      console.error("Error getting QR Code", err);
    });
  };

  onMounted(async () => {
    try {
      const [employeesResponse, groupsResponse, locationsResponse] = await Promise.all([
        axios.get("http://localhost:4200/api/employees", { withCredentials: true }),
        axios.get("http://localhost:4200/api/groups", { withCredentials: true }),
        axios.get("http://localhost:4200/api/locations", { withCredentials: true }),
      ]);

      employees.value = employeesResponse.data;
      groups.value = groupsResponse.data;
      locations.value = locationsResponse.data;

      items.value = [];
      items.value = employees.value.map((employee) => {
        const group = groups.value.find((g) => g.id === employee.group_id);
        const groupName = group ? group.group_name : "Unbekannt";
        const groupId = group ? group.id : null;
        const locationId = group ? group.location_id : null;

        const location = locations.value.find((l) => l.id === (group ? group.location_id : null));
        const locationName = location ? location.location_name : "Unbekannt";
        return {
          id: employee.id,
          first_name: employee.first_name,
          last_name: employee.last_name,
          employee_number: employee.employee_number,
          group_id: employee.group_id,
          group_id: groupId,
          group_name: groupName,
          location_id: locationId,
          location_name: locationName,
        };
      });
      console.log(items.value);
    } catch (err) {
      console.error("Error fetching data", err);
    }
  });
 
  const headers = ref([
     { title: "Nummer", key: "employee_number" },
     { title: "Nachname", key: "last_name" },
     { title: "Vorname", key: "first_name" },
     { title: "Gruppe", key: "group_name" },
     { title: "Standort", key: "location_name"},
     { title: "", key: "actions", sortable: false },]);
</script>
 