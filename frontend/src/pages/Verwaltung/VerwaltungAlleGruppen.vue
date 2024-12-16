<template>
  <NavbarVerwaltung/>
  <div class="mx-4 my-5 d-flex justify-start flex-wrap">
    <v-card class="mx-4 my-4" elevation="16" min-width="17em" max-width="17em"
      v-for="group in sortedGroups"
      :key="group.id"
    >
      <v-card-item>
        <v-btn
          icon="mdi-information-outline"
          class="position-absolute"
          style="top: 5px; right: 5px;"
          @click="showDetails(group)"
          density="compact"
        >
        </v-btn>
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
            @click="openEditDialog(group)"
          >
            <v-icon>mdi-lead-pencil</v-icon>
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

 <v-dialog v-model="editDialog" persistent max-width="400">
    <v-card>
      <v-card-title class="primary d-flex justify-start">
        <v-icon left class="mr-2"> mdi-map-marker-radius </v-icon>
        <span class="text-h5">Gruppe bearbeiten</span>
      </v-card-title>
      <v-card-text>
        <span>Neuen Gruppenleitung festlegen</span>
        <v-menu>
          <template #activator="{ props }">
            <v-text-field
              v-bind="props"
              v-model="newLeaderName"
              label="Neue Gruppenleitung"
              readonly
              append-inner-icon="mdi-chevron-down"
            ></v-text-field>
          </template>
          <v-list>
            <v-list-item v-for="leader in groupLeaders.filter(
              leader => leader.own_group === null)"
              :key="leader.id"
              @click="selectLeader(leader)"
            >
              <v-list-item-title>{{ leader?.first_name }} {{ leader?.last_name }}</v-list-item-title>
            </v-list-item>
          </v-list>
        </v-menu>
      </v-card-text>
      <v-card-actions>
        <v-btn text @click="closeEditDialog">Abbrechen</v-btn>
        <v-btn
          color="primary"
          :disabled="!form"
          type="submit"
          variant="elevated"
          @click="confirmEdit"
          >Speichern
        </v-btn>
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
        <p> Damit werden auch <strong>alle Gruppenmitglieder gelöscht!</strong></p>
      </div>
    </v-card-text>
    <v-card-actions>
      <v-btn text @click="closeDeleteDialog">Abbrechen</v-btn>
      <v-btn color="red" variant="elevated" @click="checkDelete">Löschen</v-btn>
    </v-card-actions>
  </v-card>
 </v-dialog>

 <v-dialog v-model="secondDeleteDialog" persistent max-width="600">
  <v-card>
    <v-card-title class="text-red">Gruppe und Mitglieder löschen</v-card-title>
    <v-card-text>
      <p>Es werden <strong>{{ groupToDelete?.group_name }}</strong> und folgende Mitglieder gelöscht:</p>
      <v-list density="compact">
        <v-list-item
          v-for="employee in employeesToDelete"
          :key="employee.id"
        >
          <v-list-item-title>
            {{ employee.employee_number }} - {{ employee.first_name }} {{ employee.last_name }}
          </v-list-item-title>
        </v-list-item>
      </v-list>
    </v-card-text>
    <v-card-actions>
      <v-btn text @click="closeDeleteDialog">Abbrechen</v-btn>
      <v-btn color="red" variant="elevated" @click="confirmDelete">trotzdem Löschen</v-btn>
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
const snackbarText = ref(" ");
const snackbar = ref(false);
const groups = ref(null);
const sortedGroups = ref([]);
const employees = ref(null);
const employeesToDelete = ref([]);
const detailDialog = ref(false);
const deleteDialog = ref(false);
const secondDeleteDialog = ref(false);
const selectedGroup = ref(null);
const groupToDelete = ref(null);
const selectedEmployees = ref([]);
const editDialog = ref(false);
const groupToEdit = ref(null);
const groupLeaders = ref([]);
const newLeaderID = ref(null);
const newLeaderName = ref("");
const form = ref(false);

onMounted(() => {
  axios
    .get(import.meta.env.VITE_API + "/api/groups", { withCredentials: true })
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
    .get(import.meta.env.VITE_API + "/api/users/group-leaders", { withCredentials: true })
    .then((response) => {
      groupLeaders.value = response.data;
    })
    .catch((err) => console.log(err));

  axios
  .get(import.meta.env.VITE_API + "/api/employees", { withCredentials: true })
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
};

const openEditDialog = (group) => {
  editDialog.value = true;
  groupToEdit.value = group;
};
const selectLeader = (newLeader) => {
  newLeaderID.value = newLeader.id;
  newLeaderName.value = newLeader.first_name+" "+newLeader.last_name;
  form.value = true;
};
const confirmEdit = () => {
  const updatedGroup = {
    group_name: groupToEdit.value.group_name,
    location_id: groupToEdit.value.location.id,
    user_id_group_leader: newLeaderID.value,
    user_id_replacement: groupToEdit.value.group_leader_replacement.id,
  }
  axios
    .put(import.meta.env.VITE_API + `/api/groups/${groupToEdit.value.id}`, updatedGroup, {
      withCredentials: true,
    })
    .then(() => {
      const oldLeaderID = groupToEdit.value.group_leader?.id;
      const oldLeaderIndex = groupLeaders.value.findIndex(
        (leader) => leader.id === oldLeaderID
      )
      if (oldLeaderID) {
        groupLeaders.value[oldLeaderIndex].own_group = null;
      };
      const updatedLeader = groupLeaders.value.find(
        (leader) => leader.id === newLeaderID.value
      );

      if (updatedLeader) {
        const groupIndex = groups.value.findIndex(
          (group) => group.id === groupToEdit.value.id
        );

        if (groupIndex !== -1) {
          groups.value[groupIndex].group_leader.first_name = updatedLeader.first_name;
          groups.value[groupIndex].group_leader.last_name = updatedLeader.last_name;
        }
      }
      const newLeaderIndex = groupLeaders.value.findIndex(
        (leader) => leader.id === newLeaderID.value);
      groupLeaders.value[newLeaderIndex].own_group = 0;
      closeEditDialog();
      snackbarText.value = "Die Gruppe wurde erfolgreich aktualisiert!";
      snackbar.value = true;
    })
    .catch((err) => console.log(err))
}
const closeEditDialog = () => {
  newLeaderID.value = null;
  newLeaderName.value = "";
  form.value = false;
  editDialog.value = false;
};

const handleDelete = (group) => {
  groupToDelete.value = group;
  deleteDialog.value = true;
};

const checkDelete = () => {
  if (employees.value.some(employee => employee.group?.id === groupToDelete.value.id)) {
    secondDeleteDialog.value = true;
    employeesToDelete.value = employees.value.filter(
      (employee) => employee.group.id === groupToDelete.value.id
    );
  } else {
    confirmDelete();
  }
};

const confirmDelete = () => {
  axios
    .delete(import.meta.env.VITE_API + `/api/groups/${groupToDelete.value.id}`, {
      withCredentials: true,
    })
    .then(() => {
      groups.value = groups.value.filter(
        (group) => group.id !== groupToDelete.value.id
      );
      sortedGroups.value = sortedGroups.value.filter(
        (group) => group.id !== groupToDelete.value.id
      );
      console.log(groups);
      closeDeleteDialog();
      snackbarText.value = "Die Gruppe wurde erfolgreich gelöscht!";
      snackbar.value = true;
    })
    .catch((err) => {
      console.log(err);
      secondDeleteDialog.value = true;
    });
};

const closeDeleteDialog = () => {
  deleteDialog.value = false;
  secondDeleteDialog.value = false;
  groupToDelete.value = null;
  employeesToDelete.value = [];
};
</script>
