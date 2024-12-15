<template>
  <NavbarVerwaltung/>
  <h1 class="text-center text-pink">Alle Gruppen</h1>
  <div class="mx-4 my-5 d-flex justify-start flex-wrap">
    <v-card class="mx-4 my-4" elevation="16" min-width="17em" max-width="17em"
      v-for="group in sortedGroups"
      :key="group.id"
    >
      <v-card-item>
        <div>
          <v-card-title>
            <div class="d-flex flex-column">
              <span class="text-h6 font-weight-bold text-truncate">{{ group.group_name }}</span>
              <span class="text-subtitle-2 text-truncate">Standort: {{ group.location.location_name }}</span>
            </div>
          </v-card-title>
        </div>
        <v-card-actions class="justify-end">
          <v-btn class="mt-2 bg-primary"
            @click="showDetails(group)"
          >
            <v-icon>mdi-information-outline</v-icon>
          </v-btn>
          <v-btn class="mt-2 bg-red"
            @click="handleDelete(group)"
          >
            <v-icon>mdi-trash-can-outline</v-icon>
          </v-btn>
        </v-card-actions>
      </v-card-item>
    </v-card>
 </div>
 <v-dialog v-model="detailDialog" persistent max-width="600">
  <v-card>
    <v-card-title>
      <div>
        <v-icon left class="mr-2">mdi-account-group</v-icon>
        <span class="text-h5" style="white-space: normal; word-wrap: break-word;">
          {{ selectedGroup?.group_name }} - {{ selectedGroup?.location.location_name }}
        </span>
      </div>
    </v-card-title>
    <v-card-text>
      <p><strong>Gruppenleiter:</strong>
        {{ selectedGroup?.group_leader.first_name }} {{ selectedGroup?.group_leader.last_name }}
      </p>
      <p><strong>Mitglieder:</strong></p>
      <v-data-table :headers="headers" :items="selectedEmployees">
      </v-data-table>
    </v-card-text>
    <v-card-actions>
      <v-btn color="primary" @click="closeDetailDialog">Schließen</v-btn>
    </v-card-actions>
  </v-card>
 </v-dialog>

 <v-dialog v-model="deleteDialog" persistent max-width="600">
  <v-card>
    <v-card-text>
      <div class="d-flex justify-center text-red mb-4">
        <p class="text-h5 font-weight-black" >Gruppe löschen</p>
      </div>
      <div class="text-medium-emphasis">
        <p> Sind Sie sicher, dass Sie die Gruppe
          <strong>{{ groupToDelete?.group_name }} - {{ groupToDelete?.location.location_name }}</strong>
          löschen möchten?</p>
      </div>
    </v-card-text>
    <v-card-actions>
      <v-btn text @click="closeDeleteDialog">Abbrechen</v-btn>
      <v-btn color="red" variant="elevated" @click="confirmDelete">Löschen</v-btn>
    </v-card-actions>
  </v-card>
 </v-dialog>
</template>

<script setup>
import axios from "axios";
const groups = ref(null);
const sortedGroups = ref([]);
const employees = ref(null);
const detailDialog = ref(false);
const deleteDialog = ref(false);
const selectedGroup = ref(null);
const groupToDelete = ref(null);
const selectedEmployees = ref([]);

onMounted(() => {
  axios
    .get("http://localhost:4200/api/groups", { withCredentials: true })
    .then((response) => {
      groups.value = response.data;

      sortedGroups.value = (groups.value && groups.value.length > 0)
      ? groups.value.sort((a, b) => {
          if (a.location.location_name < b.location.location_name) { return -1; }
          if (a.location.location_name > b.location.location_name) { return 1; }

          if (a.group_name < b.group_name) { return -1; }
          if (a.group_name > b.group_name) { return 1; }

          return 0;
        })
      : []
    })
    .catch((err) => console.log(err));

  axios
  .get("http://localhost:4200/api/employees", { withCredentials: true })
    .then((response) => {
      employees.value = response.data;
    })
    .catch((err) => console.log(err));
});

const headers = [
  {title: 'Nummer', key: 'employee_number'},
  {title: 'Vorname', key: 'first_name'},
  {title: 'Nachname', key: 'last_name'}
];

const showDetails = (group) => {
  selectedGroup.value = group;
  if (employees.value && employees.value.length > 0) {
    selectedEmployees.value = employees.value.filter(
      (employee) => employee.group.id == group.id
    );
  } else {
    selectedEmployees.value = [];
  }
  detailDialog.value = true;
};

const closeDetailDialog = () => {
  detailDialog.value = false;
  selectedGroup.value = null;
  selectedEmployees.value = [];
}

const handleDelete = (group) => {
  groupToDelete.value = group;
  deleteDialog.value = true;
};

const confirmDelete = () => {
  closeDeleteDialog();
}

const closeDeleteDialog = () => {
  deleteDialog.value = false;
  groupToDelete.value = null;
};
</script>
