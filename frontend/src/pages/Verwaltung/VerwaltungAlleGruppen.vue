<template>
  <NavbarVerwaltung
    :breadcrumbs="[{ title: 'Gruppen' }, { title: 'Alle Gruppen' }]"
  />
  <FilterBar
    :viewSwitcherEnabled="false"
    :filterList="[
      'group_name',
      'group_number',
      'group_leader.first_name',
      'group_leader.last_name',
      'location.location_name',
    ]"
    :items="sortGroups(groups)"
    @searchresult="updateOverview"
    @changeview=""
  />
  <div v-if="grouplist.length != 0" class="grid-container">
    <div v-for="group in grouplist" :key="group?.id" class="grid-item">
      <v-card
        class="mx-2 my-2 text-blue-grey-darken-2"
        :min-width="400"
        :max-width="400"
        elevation="16"
      >
        <v-card-item>
          <v-card-title>
            <div class="d-flex justify-space-between align-center mb-2">
              {{ group?.group_name }}
              <v-btn
                class="bg-primary mt-1 mx-1"
                @click="openDialog(group)"
                size="small"
                ><v-icon>mdi-information-outline</v-icon></v-btn
              >
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
                <span class="me-1 ml-2"
                  >{{ group?.group_leader.first_name }}
                  {{ group?.group_leader.last_name }}</span
                >
              </div>
              <div class="mt-1">
                <v-icon
                  color="primary"
                  icon="mdi-map-marker"
                  size="small"
                ></v-icon>
                <span class="me-1 ml-2">{{
                  group?.location.location_name
                }}</span>
              </div>
            </div>
          </v-card-subtitle>
        </v-card-item>
        <v-card-text>
          <v-divider></v-divider>
          <div class="mt-3 d-flex justify-space-between align-center">
            <v-chip
              prepend-icon="mdi-account-multiple"
              color="primary"
              label
              density="comfortable"
            >
              Mitgliederanzahl: {{ group?.employees.length }}
            </v-chip>
            <div class="d-flex ga-1 justify-end">
              <v-btn
                class="bg-primary mx-1"
                @click="openEditDialog(group)"
                size="default"
                density="comfortable"
                ><v-icon>mdi-lead-pencil</v-icon></v-btn
              >
              <v-btn
                class="bg-red"
                @click="handleDelete(group)"
                size="default"
                density="comfortable"
                ><v-icon>mdi-trash-can-outline</v-icon></v-btn
              >
            </div>
          </div>
        </v-card-text>
      </v-card>
    </div>
  </div>

  <v-dialog v-model="detailDialog" max-width="600" max-height="600" scrollable>
    <v-card class="text-blue-grey">
      <v-card-title color="primary">
        <div class="text-center mt-4">
          <v-chip color="primary" label>
            <p class="text-h5 font-weight-black">
              {{ selectedGroup?.group_name }}
            </p>
          </v-chip>
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
              <p class="font-weight-black">Gruppe</p>
            </div>
            <div class="ml-5 mb-4 text-medium-emphasis">
              <p color="text-primary">
                Gruppennummer: {{ selectedGroup?.group_number }}
              </p>
              <p color="text-primary">
                Standort: {{ selectedGroup?.location.location_name }}
              </p>
              <p color="text-primary">
                Mitgliederanzahl: {{ selectedGroup?.employees.length }}
              </p>
            </div>
            <v-divider></v-divider>
            <div class="text-left ml-4 mb-2 mt-4">
              <p class="font-weight-black">Gruppenleitung</p>
            </div>
            <div class="ml-5 text-medium-emphasis">
              <p color="text-primary">
                Vorname: {{ selectedGroup?.group_leader.first_name }}
              </p>
              <p color="text-primary">
                Nachname: {{ selectedGroup?.group_leader.last_name }}
              </p>
              <p color="text-primary">
                Benutzername: {{ selectedGroup?.group_leader.username }}
              </p>
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
            <v-data-table-virtual
              :items="selectedGroup?.employees"
              :search="search"
              :headers="headers"
              :sort-by="sortBy"
              :hover="true"
              density="compact"
            >
            </v-data-table-virtual>
          </v-tabs-window-item>
        </v-tabs-window>
      </v-card-text>
      <v-card-actions>
        <div class="d-flex justify-end ga-1">
          <v-btn class="mt-2 bg-primary" @click="closeDialog"
            ><v-icon>mdi-close-thick</v-icon></v-btn
          >
        </div>
      </v-card-actions>
    </v-card>
  </v-dialog>

  <v-dialog v-model="editDialog" max-width="400">
    <v-card class="text-blue-grey-darken-3">
      <v-card-title class="ms-2 mt-2 mb-1 text-primary d-flex justify-start">
        <v-icon left class="mr-2 mb-n3"> mdi-account-group </v-icon>
        <div class="d-flex h-100 align-center">
          <v-icon size="18" left class="mr-3 mb-n9 ms-n1">
            mdi-lead-pencil
          </v-icon>
        </div>
        <h3>Gruppe bearbeiten</h3>
      </v-card-title>
      <v-card-text>
        <v-menu>
          <template #activator="{ props }">
            <v-text-field
              :active="true"
              base-color="blue-grey"
              color="primary"
              variant="outlined"
              v-bind="props"
              v-model="newLeaderName"
              label="Gruppenleitung"
              placeholder="Neue Leitung zuweisen"
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
                {{ leader?.last_name }}
              </v-list-item-title>
            </v-list-item>
            <v-list-item
              v-if="
                groupLeaders.filter((leader) => leader.own_group === null)
                  .length < 1
              "
              disabled
              >Keine freien Gruppenleiter verfügbar {{
            }}</v-list-item>
          </v-list>
        </v-menu>
      </v-card-text>
      <v-card-actions class="mb-2 mt-5">
        <v-btn class="blue-grey" text @click="closeEditDialog">{{
          form ? "Abbrechen" : "Zurück"
        }}</v-btn>
        <v-btn
          class="me-4"
          color="primary"
          :disabled="!form"
          type="submit"
          variant="elevated"
          @click="confirmEdit"
          >Übernehmen
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
      <v-card-text>
        <div class="d-flex justify-center text-red mb-4">
          <p class="text-h5 font-weight-black">Gruppe und Mitglieder löschen</p>
        </div>
        <div class="text-medium-emphasis">
          <p>
            Es werden <strong>{{ groupToDelete?.group_name }}</strong> und
            folgende Mitglieder gelöscht:
          </p>
          <li class="mt-2 mb-2" v-for="employee in employeesToDelete">
            {{ employee.employee_number }} - {{ employee.first_name }}
            {{ employee.last_name }}
          </li>
        </div>
      </v-card-text>
      <v-card-actions>
        <v-btn text @click="closeDeleteDialog">Abbrechen</v-btn>
        <v-btn color="red" variant="elevated" @click="confirmDelete"
          >trotzdem Löschen</v-btn
        >
      </v-card-actions>
    </v-card>
  </v-dialog>
  <NoResult v-if="grouplist.length === 0 && groups.length !== 0" />
</template>

<script setup>
import FilterBar from "@/components/SearchComponents/FilterBar.vue";
import NoResult from "@/components/SearchComponents/NoResult.vue";
import axios from "axios";
import { useFeedbackStore } from "@/stores/feedback";
const feedbackStore = useFeedbackStore();
const groups = ref([]);
const grouplist = ref([]);
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

const getData = () => {
  axios
    .get(import.meta.env.VITE_API + "/api/groups/with-employees", {
      withCredentials: true,
    })
    .then((response) => {
      groups.value = sortGroups(response.data);
      grouplist.value = Object.values(sortGroups(response.data));
      grouplist.value.sort((a, b) =>
        a.group_name.toLowerCase() > b.group_name.toLowerCase()
          ? 1
          : b.group_name.toLowerCase() > a.group_name.toLowerCase()
          ? -1
          : 0
      );
    })
    .catch((err) => {
      console.error("Error fetching data", err);
      feedbackStore.setFeedback(
        "error",
        "snackbar",
        err.response?.data?.title,
        err.response?.data?.description
      );
    });
  axios
    .get(import.meta.env.VITE_API + "/api/users/group-leaders", {
      withCredentials: true,
    })
    .then((response) => {
      groupLeaders.value = response.data;
    })
    .catch((err) => {
      console.error("Error fetching data", err);
      feedbackStore.setFeedback(
        "error",
        "snackbar",
        err.response?.data?.title,
        err.response?.data?.description
      );
    });

  axios
    .get(import.meta.env.VITE_API + "/api/employees", { withCredentials: true })
    .then((response) => {
      employees.value = response.data;
    })
    .catch((err) => {
      console.error("Error fetching data", err);
      feedbackStore.setFeedback(
        "error",
        "snackbar",
        err.response?.data?.title,
        err.response?.data?.description
      );
    });
};

const headers = [
  { title: "Nummer", key: "employee_number" },
  { title: "Nachname", key: "last_name" },
  { title: "Vorname", key: "first_name" },
];

const sortBy = [{ key: "employee_number", order: "asc" }];

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
  const updatedGroup = {
    group_name: groupToEdit.value.group_name,
    group_number: groupToEdit.value.group_number,
    location_id: groupToEdit.value.location.id,
    user_id_group_leader: newLeaderID.value,
  };
  console.log(updatedGroup);
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
      getData();
      closeEditDialog();
      feedbackStore.setFeedback(
        "success",
        "snackbar",
        "",
        "Die Gruppe wurde erfolgreich aktualisiert!"
      );
    })
    .catch((err) => {
      console.error("Error editing group", err);
      feedbackStore.setFeedback(
        "error",
        "snackbar",
        err.response?.data?.title,
        err.response?.data?.description
      );
    });
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
      console.log(groups);
      closeDeleteDialog();
      feedbackStore.setFeedback(
        "success",
        "snackbar",
        "",
        "Die Gruppe wurde erfolgreich gelöscht!"
      );
      getData();
    })
    .catch((err) => {
      console.error("Error deleting group", err);
      feedbackStore.setFeedback(
        "error",
        "snackbar",
        err.response?.data?.title,
        err.response?.data?.description
      );
    });
};

const closeDeleteDialog = () => {
  deleteDialog.value = false;
  secondDeleteDialog.value = false;
  groupToDelete.value = null;
  employeesToDelete.value = [];
};

const updateOverview = (items) => {
  grouplist.value = sortGroups(items);
};

const sortGroups = (array) => {
  if (!array || array.length === 0) {
    return [];
  }
  return [...array].sort((a, b) => {
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
  });
};
getData();
</script>

<style scoped>
.grid-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(405px, 1fr));
  gap: 10px;
  justify-content: center;
  justify-items: center;
  padding: 20px;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

.grid-item {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  min-width: 400px;
  max-width: 405px;
}
</style>
