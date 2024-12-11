<template>
  <NavbarVerwaltung/>
  <div class="mx-4 my-5 d-flex justify-start flex-wrap">
    <v-card class="mx-4 my-4" elevation="16" min-width="20em" max-width="20em"
      v-for="location in locations"
    >
      <v-card-item>
        <v-card-title>
          <div class="d-flex flex-column">
            <span class="text-h6 font-weight-bold text-truncate">
              Standort: {{ location?.name }}
            </span>
            <span class="text-subtitle-2 text-truncate">
              Standortleiter: {{ getLocationLeader(location?.locationLeaderID) }}
            </span>
          </div>
        </v-card-title>
        <v-card-actions class="justify-end">
          <v-btn class="mt-2 bg-primary"
            @click="openEditDialog(location)"
          >
            <v-icon>mdi-lead-pencil</v-icon>
          </v-btn>
          <v-btn class="mt-2 bg-red"
            @click="handleDelete(location)"
          >
            <v-icon>mdi-trash-can-outline</v-icon>
          </v-btn>
        </v-card-actions>
      </v-card-item>
    </v-card>
  </div>

  <v-dialog v-model="editDialog" persistent max-width="400">
    <v-card>
      <v-card-title class="primary d-flex justify-start">
        <v-icon left class="mr-2"> mdi-map-marker-radius </v-icon>
        <span class="text-h5">Standort bearbeiten</span>
      </v-card-title>
      <v-card-text>
        <span>Neue Standortleitung festlegen</span>
        <v-menu>
          <template #activator="{ props }">
            <v-text-field
              v-bind="props"
              v-model="newLocationLeaderName"
              label="Neue Standortleitung"
              readonly
              append-inner-icon="mdi-chevron-down"
            ></v-text-field>
          </template>
          <v-list>
            <v-list-item v-for="leader in locationLeaders"
              :key="leader.userID"
              @click="selectLeader(leader)"
            >
              <v-list-item-title>{{ leader?.firstName }} {{ leader?.lastName }}</v-list-item-title>
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
        <p class="text-h5 font-weight-black" >Standort löschen</p>
      </div>
      <div class="text-medium-emphasis">
        <p> Sind Sie sicher, dass Sie den Standort <strong>{{ locationToDelete?.name }}</strong> löschen möchten?</p>
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
const newLocationLeaderID = ref(null);
const newLocationLeaderName = ref("");
const form = ref(false);
const editDialog = ref(false);
const locationToEdit = ref(null);
const deleteDialog = ref(false);
const locationToDelete = ref(null);

const locations = [{name: "W1", locationID: 293, locationLeaderID: 435},
  {name: "W8", locationID: 253, locationLeaderID: 1},
  {name: "W13", locationID: 23, locationLeaderID: 2},
  {name: "Zedtlitz", locationID: 29, locationLeaderID: 3}];

const locationLeaders = [{firstName: "Hanz", lastName: "Scheibe", userID: 435},
{firstName: "Franz", lastName: "Weise", userID: 1},
{firstName: "Glanz", lastName: "Schneise", userID: 2},
{firstName: "Natan", lastName: "Der Weise", userID: 3}];

const getLocationLeader = (leaderID) => {
  const leader = locationLeaders.find((l) => l.userID === leaderID);
  return leader ? `${leader.firstName} ${leader.lastName}` : "Not Found";
};

const openEditDialog = (location) => {
  editDialog.value = true;
  locationToEdit.value = location;
};
const closeEditDialog = () => {
  editDialog.value = false;
  locationToEdit.value = null;
  newLocationLeaderID.value = null;
  form.value = false;
  newLocationLeaderName.value = "";
};
const selectLeader = (newLeader) => {
  newLocationLeaderID.value = newLeader.userID;
  newLocationLeaderName.value = newLeader.firstName+" "+newLeader.lastName;
  form.value = true;
};

const handleDelete = (location) => {
  locationToDelete.value = location;
  deleteDialog.value = true;
};
const closeDeleteDialog = () => {
  locationToDelete.value = null;
  deleteDialog.value = false;
};
const confirmDelete = () => {

};

</script>
