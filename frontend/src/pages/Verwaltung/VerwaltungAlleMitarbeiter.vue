<template>
  <NavbarVerwaltung />
  <FilterBar
    :viewSwitcherEnabled="false"
    :filterList="['first_name', 'last_name', 'employee_number', 'group_name', 'location_name']"
    :items="employees"
    @searchresult="updateOverview"
  >
    <template #outside>
      <transition name="fade-toolbar" mode="out-in" style="width: 70%;">
        <v-toolbar v-if="selected.length > 0 && items.length > 0" color="grey-lighten-2" flat dark density="compact" rounded="lg">
          <v-btn class="ml-3 mr-3" icon="mdi-close" density="compact" @click="selected = []"></v-btn>
          <v-divider inset vertical></v-divider>
          <p class="ml-4 mr-2">{{ selected.length }} ausgewählt</p>
          <v-spacer></v-spacer>
          <v-btn prepend-icon="mdi-qrcode" class="bg-green mr-2" @click="getQRCodeSelected" size="small">QR Codes generieren</v-btn>
          <v-btn prepend-icon="mdi-trash-can-outline" class="bg-red mr-2" @click="opendeleteDialogSelected" size="small">Ausgewählte Mitarbeiter löschen</v-btn>
        </v-toolbar>

        <v-toolbar v-else-if="selected.length == 0" color="white" flat dark density="compact" rounded="lg">
          <p class="text-h6">Anzahl aller jetzigen Mitarbeiter: {{ employees.length }}</p>
          <v-spacer></v-spacer>
          <v-btn prepend-icon="mdi-reload" @click="fetchData">Neuladen</v-btn>
        </v-toolbar>
      </transition>
    </template>
  </FilterBar>
  <v-container style="width: 70%;">
    <div v-if="items.length > 0">
      <v-data-table v-model="selected" :headers="headers"  :items="items" :sort-by="sortBy" :loading="loading" :hover="true" item-value="id" show-select items-per-page="15" items-per-page-text="Einträge pro Seite" page-text="" show-current-page :items-per-page-options="itemsPerPage">
      <template v-slot:[`item.actions`]="{ item }">
        <v-btn icon="mdi-qrcode" class="bg-green mr-2" @click="getQRCode(item)" size="small" :disabled="selected.length > 0"></v-btn>
        <v-btn icon="mdi-lead-pencil" class="bg-primary mr-2" @click="openeditDialog(item)" size="small" :disabled="selected.length > 0"></v-btn>
        <v-btn icon="mdi-trash-can-outline" class="bg-red" @click="opendeleteDialog(item)" size="small" :disabled="selected.length > 0"></v-btn>
      </template>
      </v-data-table>
    </div>
    <NoResult v-else-if="items.length == 0 && employees.length != 0" />
  </v-container>
  <v-dialog v-model="deleteDialog" persistent max-width="400">
    <v-card>
      <v-card-text>
        <div class="d-flex justify-center text-red mb-7">
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
  <v-dialog v-model="deleteDialogSelected" persistent max-width="500">
    <v-card>
      <v-card-text>
        <div class="d-flex justify-center text-red mb-7">
          <p class="text-h5 font-weight-black" >Ausgewählte Mitarbeiter löschen</p>
        </div>
        <div class="text-medium-emphasis">
          <p class="mb-2"> Sind Sie sicher, dass Sie folgende Mitarbeiter löschen möchten?</p>
          <p />
          <li v-for="employee in employeesToDelete" :key="employee.id"><strong> {{ employee.first_name }} {{ employee.last_name }} </strong> </li>
        </div>
      </v-card-text>
      <v-card-actions>
        <v-btn text @click="closedeleteDialogSelected">Abbrechen</v-btn>
        <v-btn color="red" variant="elevated" @click="confirmDeleteSelected">Löschen</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
  <v-dialog v-model="editDialog" persistent max-width="500">
      <v-card>
      <v-card-text>
        <div class="d-flex justify-center text-primary mb-7">
          <p class="text-h5 font-weight-black">Mitarbeiter bearbeiten</p>
        </div>
        <div>
          <v-form ref="validation" v-model="form">
            <v-text-field
              v-model="employee_number"
              :rules="[required]"
              label="Kunden-Nr."
              clearable
            ></v-text-field>
            <v-text-field
              v-model="first_name"
              :rules="[required]"
              label="Vorname"
              clearable
            ></v-text-field>
            <v-text-field
              v-model="last_name"
              :rules="[required]"
              label="Nachname"
              clearable
            ></v-text-field>
            <v-menu offset-y>
              <template #activator="{ props }">
                <v-text-field
                  v-bind="props"
                  v-model="group_name"
                  label="Gruppen Name"
                  readonly
                  append-inner-icon="mdi-chevron-down"
                ></v-text-field>
              </template>
              <v-list>
                <v-list-item v-for="location in locations" :key="location.name">
                  <v-list-item-title>{{ location.name }}</v-list-item-title>
                  <template v-slot:append>
                    <v-icon icon="mdi-menu-right" size="x-small"></v-icon>
                  </template>
                  <v-menu
                    offset-y
                    activator="parent"
                    open-on-click
                    open-on-hover
                    close-on-content-click
                    location="end"
                  >
                    <v-list>
                      <v-list-item
                        v-for="group in location.groups"
                        :key="group.name"
                        @click="selectOption(group.name, location.name)"
                      >
                        <v-list-item-title>{{ group.name }}</v-list-item-title>
                      </v-list-item>
                    </v-list>
                  </v-menu>
                </v-list-item>
              </v-list>
            </v-menu>
          </v-form>
        </div>
      </v-card-text>
      <v-card-actions>
        <v-btn @click="closeeditDialog">Abbrechen</v-btn>
        <v-btn
          color="primary"
          type="submit"
          variant="elevated"
          :disabled="!form"
          @click="submitForm"
          >Speichern</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
  <SuccessSnackbar
    v-model="snackbar"
    :text="snackbarText"
  ></SuccessSnackbar>
  <ErrorSnackbar
    v-model="errorSnackbar"
    :text="errorSnackbarText"
    @close="errorSnackbar = false"
  ></ErrorSnackbar>
</template>


<script setup>
  import axios from "axios";
  const loading = ref(true);
  const deleteDialog = ref(false);
  const editDialog = ref(false);
  const deleteDialogSelected = ref(false);
  const employeeToDelete = ref("");
  const employeeToDeleteID = ref("");
  const employeeToEditID = ref("");
  const employeesToDelete = ref([]);
  const snackbar = ref(false);
  const snackbarText = ref("");
  const errorSnackbar = ref(false);
  const errorSnackbarText = ref("");
  const items = ref([]);
  const employees = ref([]);
  const locations = ref([]);
  const itemsPerPage = ref([{value: 15, title: '15'}, {value: 30, title: '30'},{value: 50, title: '50'}, {value: 100, title: '100'}, {value: -1, title: 'Alle Einträge'}]);

  const employee_number = ref('');
  const first_name = ref('');
  const last_name = ref('');
  const group_name = ref('');
  const location_name = ref('');
  const validation = ref(null);
  const form = ref(false);

  const selected = ref([]);

  const opendeleteDialog = (item) => {
    employeeToDelete.value = item.first_name  + " " + item.last_name;
    employeeToDeleteID.value = item.id;
    deleteDialog.value= true;
  };

  const closedeleteDialog = () => {
    deleteDialog.value = false;
  };

  const opendeleteDialogSelected = () => {
    employeesToDelete.value = employees.value
    .filter(emp => selected.value.includes(emp.id))
    .map(emp => ({ id: emp.id, first_name: emp.first_name, last_name: emp.last_name }));
    deleteDialogSelected.value = true;
  };

  const closedeleteDialogSelected = () => {
    deleteDialogSelected.value = false;
  };

  const openeditDialog = (item) => {
    fetchGroups();
    employeeToEditID.value = item.id;
    const employee = items.value.find((item) => item.id === employeeToEditID.value);
    employee_number.value = employee.employee_number;
    first_name.value = employee.first_name;
    last_name.value = employee.last_name;
    group_name.value = employee.group_name;
    location_name.value = employee.location_name;
    editDialog.value= true;
  };

  const closeeditDialog = () => {
    editDialog.value = false;
  };

  const confirmDelete = () => {
    axios
      .delete(`${import.meta.env.VITE_API}/api/employees/${employeeToDeleteID.value}`, { withCredentials: true })
      .then(() => {
        deleteDialog.value = false;
        snackbar.value = false;
        snackbarText.value = `${employeeToDelete.value} wurde erfolgreich gelöscht!`;
        snackbar.value = true;
        fetchData();
      })
      .catch((err) => {
        console.error(err);
        errorSnackbarText.value = `Fehler beim löschen von ${employeeToDelete.value}`;
        errorSnackbar.value = true;
      })
  };

  const confirmDeleteSelected = () => {
    axios
      .delete(`${import.meta.env.VITE_API}/api/employees/`, { data: { employee_ids: selected.value }, withCredentials: true })
      .then(() => {
        deleteDialogSelected.value = false;
        snackbar.value = false;
        snackbarText.value = "Die ausgewählten Mitarbeiter wurden erfolgreich gelöscht!";
        snackbar.value = true;
        selected.value = [];
        fetchData();
      })
      .catch((err) => {
        console.error(err);
        errorSnackbarText.value = "Fehler beim löschen der ausgewählten Mitarbeiter!";
        errorSnackbar.value = true;
      });
  }

  const getQRCodeSelected = () => {
    axios
      .post(`${import.meta.env.VITE_API}/api/employees/qr-codes-by-list`, 
      { employee_ids: selected.value }, { responseType: "blob", withCredentials: true })
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
        snackbarText.value = "Die QR-Codes wurden erfolgreich generiert!";
        snackbar.value = true;
      })
      .catch((err) => {
        console.error("Error getting QR Codes", err);
        errorSnackbarText.value = "Fehler beim generieren der QR-Codes!"
        errorSnackbar.value = true;
      });
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
      errorSnackbarText.value = "Fehler beim generieren des QR-Codes!"
      errorSnackbar.value = true;
    });
  };

  const fetchData = () => {
    loading.value = true;
    axios
    .get(import.meta.env.VITE_API + "/api/employees", { withCredentials: true })
    .then((response) => {
      items.value = response.data.map((employee) => {
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
      employees.value = items.value;
      loading.value = false;
    })
    .catch((err) => console.error("Error fetching data", err));
  };

  const updateOverview = (list) => {
    items.value = list;
  };

  onMounted(() => {
    fetchData();
  });

  const headers = [
     { title: "Nummer", key: "employee_number", nowrap: true},
     { title: "Vorname", key: "first_name", nowrap: true },
     { title: "Nachname", key: "last_name", nowrap: true },
     { title: "Gruppe", key: "group_name", nowrap: true },
     { title: "Standort", key: "location_name", nowrap: true},
     { title: "", key: "actions", sortable: false, nowrap: true },];
  const sortBy = [{ key: 'employee_number', order: 'asc' }]

  const fetchGroups = () => {
    axios
      .get(import.meta.env.VITE_API + "/api/groups/with-locations", { withCredentials: true })
      .then((response) => {
        const groupsData = response.data;
        locations.value = Object.entries(groupsData).map(([locationName, groupNames]) => {
          return {
            name: locationName,
            groups: groupNames.map((groupName) => ({
              name: groupName,
            })),
          };
        });
      })
      .catch((err) => console.error("Error fetching groups", err));
  };

  const required = (v) => {
    return !!v || "Eingabe erforderlich";
  };

  const selectOption = (selectedGroup, location) => {
    group_name.value = selectedGroup;
    location_name.value = location;
  };

  const submitForm = () => {
      const payload = {
        employee_number: employee_number.value,
        first_name: first_name.value,
        last_name: last_name.value,
        group_name: group_name.value,
        location_name: location_name.value,
      }

      axios
        .put(`${import.meta.env.VITE_API}/api/employees/${employeeToEditID.value}`, payload, { withCredentials: true })
        .then(() => {
          fetchData();
          closeeditDialog();
          snackbar.value = false;
          snackbarText.value = `${payload.first_name} ${payload.last_name} wurde erfolgreich aktualisiert!`;
          snackbar.value = true;
          deleteDialog.value = false;
        })
        .catch((err) => {
          console.error("Error updating employee", err);
          errorSnackbarText.value = `Fehler beim aktualisieren von ${payload.first_name} ${payload.last_name}`;
          errorSnackbar.value = true;
        });
  };
</script>


<style scoped>
.fade-toolbar-enter-active,
.fade-toolbar-leave-active {
  transition: opacity 0.2s ease, transform 0.1s ease;
}

.fade-toolbar-enter-from {
  opacity: 0;
  transform: translateY(-5px);
}

.fade-toolbar-leave-to {
  opacity: 0;
  transform: translateY(5px);
}
</style>