<template>
  <NavbarVerwaltung />
  <div class="ml-10 mr-10 mt-5">
      <v-row class="d-flex justify-start">
        <v-col
          v-for="group in groups"
          :key="group?.id"
          cols="12" sm="12" md="6" lg="4" xl="3" xxl = "2"
          class="d-flex justify-center"
        >
          <v-card class="mx-2 my-2" width="450" elevation="16">
            <v-card-item>
                <v-card-title>
                  <div class="mt-3 d-flex justify-space-between align-center">
                    {{ group?.group_name }}
                    <v-btn class="bg-primary mx-1" @click="openDialog(group)" size="small"><v-icon>mdi-information-outline</v-icon></v-btn>
                  </div>
                </v-card-title>
                <v-card-subtitle>
                  <div class="d-flex flex-column">
                    <div>
                      <v-icon
                      color="primary"
                      icon="mdi-account-circle"
                      size="small"
                      ></v-icon>
                      <span class="me-1 ml-2">{{ group?.group_leader.first_name }} {{ group?.group_leader.last_name }}</span>
                    </div>
                    <div>
                      <v-icon
                      color="primary"
                      icon="mdi-map-marker"
                      size="small"
                      ></v-icon>
                      <span class="me-1 ml-2">{{ group?.location.location_name }}</span>
                    </div>
                  </div>
                </v-card-subtitle>
            </v-card-item>
            <v-card-text>
                <v-divider></v-divider>
                <div class="mt-3 d-flex justify-space-between align-center">
                    <v-chip prepend-icon="mdi-account-multiple" color="primary" label density="compact"> Mitgliederanzahl: {{group?.employees.length}} </v-chip>
                    <div class="d-flex">
                      <v-btn class="bg-primary mx-1" @click="openEditDialog(group)" size="small"><v-icon>mdi-lead-pencil</v-icon></v-btn>
                      <v-btn class="bg-red" @click="handleDelete(group)" size="small"><v-icon>mdi-trash-can-outline</v-icon></v-btn>
                    </div>
                </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </div>

  <v-dialog v-model="detailDialog" max-width="600" max-height="600" scrollable>
    <v-card>
        <v-card-title color="primary">
            <div class="text-center mt-4">
                <v-chip color="primary" label> <p class="text-h5 font-weight-black"> {{ selectedGroup?.group_name }} </p> </v-chip>
            </div>
        </v-card-title>
        <div class="mb-2">
            <v-tabs v-model="tab" align-tabs="center" color="primary">
                <v-tab value="one">Übersicht</v-tab>
                <v-tab value="two">Mitglieder</v-tab>
            </v-tabs>
        </div>

        <v-card-text>
            <v-tabs-window v-model="tab">
                <v-tabs-window-item value="one">
                    <div class="text-left ml-4 mb-2 mt-2">
                        <p class="font-weight-black"> Gruppe </p>
                    </div>
                    <div class="ml-5 mb-4 text-medium-emphasis">
                        <p color="text-primary"> Standort: {{ selectedGroup?.location.location_name }}</p>
                        <p color="text-primary"> Mitgliederanzahl: {{selectedGroup?.employees.length}} </p>
                    </div>
                    <v-divider></v-divider>
                    <div class="text-left ml-4 mb-2 mt-4">
                        <p class="font-weight-black"> Gruppenleitung </p>
                    </div>
                    <div class="ml-5 text-medium-emphasis">
                        <p color="text-primary"> Vorname: {{selectedGroup?.group_leader.first_name}} </p>
                        <p color="text-primary"> Nachname: {{selectedGroup?.group_leader.last_name}} </p>
                        <p color="text-primary"> Benutzername: {{selectedGroup?.group_leader.username}} </p>
                    </div>
                </v-tabs-window-item>

                <v-tabs-window-item value="two">
                    <v-text-field
                        v-model="search"
                        density="compact"
                        label="Suche"
                        prepend-inner-icon="mdi-magnify"
                        variant="solo-filled"
                        flat
                        hide-details
                        clearable
                        single-line
                        rounded
                    ></v-text-field>
                    <v-data-table-virtual :items="selectedGroup?.employees" :search="search" :headers="headers" :sort-by="sortBy" :hover="true" density="compact">
                    </v-data-table-virtual>
                </v-tabs-window-item>
            </v-tabs-window>
        </v-card-text>
        <v-card-actions>
            <div class="d-flex justify-end ga-1">
                <v-btn class="mt-2 bg-primary" @click="closeDialog"><v-icon>mdi-close-thick</v-icon></v-btn>
            </div>
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
        <span>Neue Gruppenleitung festlegen</span>
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
            <v-list-item
              v-for="leader in groupLeaders.filter(
                (leader) => leader.own_group === null
              )"
              :key="leader.id"
              @click="selectLeader(leader)"
            >
              <v-list-item-title
                >{{ leader?.first_name }}
                {{ leader?.last_name }}</v-list-item-title
              >
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
          <p class="text-h5 font-weight-black">Gruppe löschen</p>
        </div>
        <div class="text-medium-emphasis">
          <p>
            Sind Sie sicher, dass Sie die Gruppe
            <strong
              >{{ groupToDelete?.group_name }} -
              {{ groupToDelete?.location.location_name }}</strong
            >
            löschen möchten?
          </p>
          <p>
            Damit werden auch <strong>alle Gruppenmitglieder gelöscht!</strong>
          </p>
        </div>
      </v-card-text>
      <v-card-actions>
        <v-btn text @click="closeDeleteDialog">Abbrechen</v-btn>
        <v-btn color="red" variant="elevated" @click="checkDelete"
          >Löschen</v-btn
        >
      </v-card-actions>
    </v-card>
  </v-dialog>

  <v-dialog v-model="secondDeleteDialog" persistent max-width="600">
    <v-card>
      <v-card-title class="text-red"
        >Gruppe und Mitglieder löschen</v-card-title
      >
      <v-card-text>
        <p>
          Es werden <strong>{{ groupToDelete?.group_name }}</strong> und
          folgende Mitglieder gelöscht:
        </p>
        <v-list density="compact">
          <v-list-item v-for="employee in employeesToDelete" :key="employee.id">
            <v-list-item-title>
              {{ employee.employee_number }} - {{ employee.first_name }}
              {{ employee.last_name }}
            </v-list-item-title>
          </v-list-item>
        </v-list>
      </v-card-text>
      <v-card-actions>
        <v-btn text @click="closeDeleteDialog">Abbrechen</v-btn>
        <v-btn color="red" variant="elevated" @click="confirmDelete"
          >trotzdem Löschen</v-btn
        >
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
const editDialog = ref(false);
const groupToEdit = ref(null);
const groupLeaders = ref([]);
const newLeaderID = ref(null);
const newLeaderName = ref("");
const form = ref(false);

const tab = ref("");
const search = ref("");

onMounted(() => {
  axios
    .get(import.meta.env.VITE_API + "/api/groups/with-employees", { withCredentials: true })
    .then((response) => {
      groups.value = response.data;

      sortedGroups.value =
        groups.value && groups.value.length > 0
          ? groups.value.sort((a, b) => {
              if (a.location.location_name < b.location.location_name) {
                return -1;
              }
              if (a.location.location_name > b.location.location_name) {
                return 1;
              }

              if (a.group_name < b.group_name) {
                return -1;
              }
              if (a.group_name > b.group_name) {
                return 1;
              }

              return 0;
            })
          : [];
    })
    .catch((err) => console.log(err));
  axios
    .get(import.meta.env.VITE_API + "/api/users/group-leaders", {
      withCredentials: true,
    })
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
  { title: "Nummer", key: "employee_number"},
  { title: "Nachname", key: "last_name" },
  { title: "Vorname", key: "first_name" },
];

const sortBy = [{ key: 'employee_number', order: 'asc' }]

const openDialog = (group) => {
    detailDialog.value = true;
    selectedGroup.value = group;
};

const closeDialog = () => {
    detailDialog.value = false;
    selectedGroup.value = null;
};

const openEditDialog = (group) => {
  editDialog.value = true;
  groupToEdit.value = group;
};
const selectLeader = (newLeader) => {
  newLeaderID.value = newLeader.id;
  newLeaderName.value = newLeader.first_name + " " + newLeader.last_name;
  form.value = true;
};
const confirmEdit = () => {
  console.log(groupToEdit.value.group_leader_replacement)
  const updatedGroup = {
    group_name: groupToEdit.value.group_name,
    location_id: groupToEdit.value.location.location_id,
    user_id_group_leader: newLeaderID.value,
    user_id_replacement: groupToEdit.value.group_leader_replacement?.id || null,
  };
  axios
    .put(
      import.meta.env.VITE_API + `/api/groups/${groupToEdit.value.id}`,
      updatedGroup,
      {
        withCredentials: true,
      }
    )
    .then(() => {
      const oldLeaderID = groupToEdit.value.group_leader?.id;
      const oldLeaderIndex = groupLeaders.value.findIndex(
        (leader) => leader.id === oldLeaderID
      );
      if (oldLeaderID) {
        groupLeaders.value[oldLeaderIndex].own_group = null;
      }
      const updatedLeader = groupLeaders.value.find(
        (leader) => leader.id === newLeaderID.value
      );

      if (updatedLeader) {
        const groupIndex = groups.value.findIndex(
          (group) => group.id === groupToEdit.value.id
        );

        if (groupIndex !== -1) {
          groups.value[groupIndex].group_leader.first_name =
            updatedLeader.first_name;
          groups.value[groupIndex].group_leader.last_name =
            updatedLeader.last_name;
        }
      }
      const newLeaderIndex = groupLeaders.value.findIndex(
        (leader) => leader.id === newLeaderID.value
      );
      groupLeaders.value[newLeaderIndex].own_group = 0;
      closeEditDialog();
      snackbarText.value = "Die Gruppe wurde erfolgreich aktualisiert!";
      snackbar.value = true;
    })
    .catch((err) => console.log(err));
};
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
  if (
    employees.value.some(
      (employee) => employee.group?.id === groupToDelete.value.id
    )
  ) {
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
    .delete(
      import.meta.env.VITE_API + `/api/groups/${groupToDelete.value.id}`,
      {
        withCredentials: true,
      }
    )
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
