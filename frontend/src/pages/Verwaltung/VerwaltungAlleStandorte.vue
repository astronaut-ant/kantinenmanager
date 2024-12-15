<template>
  <NavbarVerwaltung/>
  <div class="mx-4 my-5 d-flex justify-start flex-wrap">
    <v-card class="mx-4 my-4" elevation="16" min-width="20em" max-width="20em"
      v-for="location in locations" :key="location?.id"
    >
      <v-card-item>
        <v-card-title>
          <div class="d-flex flex-column">
            <span class="text-h6 font-weight-bold text-truncate">
              Standort: {{ location?.location_name }}
            </span>
            <span class="text-subtitle-2 text-truncate">
              Standortleiter:
              {{ location?.location_leader.first_name }} {{ location?.location_leader.last_name }}
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
            <v-list-item v-for="leader in locationLeaders.filter(
        (leader) => leader.id !== locationToEdit.location_leader.id)"
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
          @click="confirmEdit(locationToEdit,)"
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
        <p> Sind Sie sicher, dass Sie den Standort <strong>{{ locationToDelete?.location_name }}</strong> löschen möchten?</p>
      </div>
    </v-card-text>
    <v-card-actions>
      <v-btn text @click="closeDeleteDialog">Abbrechen</v-btn>
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
const snackbarText = ref(" ");
const snackbar = ref(false);
const locations = ref({});
const locationLeaders = ref({});
const newLocationLeaderID = ref(null);
const newLocationLeaderName = ref("");
const form = ref(false);
const editDialog = ref(false);
const locationToEdit = ref(null);
const deleteDialog = ref(false);
const locationToDelete = ref(null);

onMounted(() => {
  axios
    .get("http://localhost:4200/api/locations", { withCredentials: true })
    .then((response) => {
      locations.value = response.data;
      // console.log(locations.value);
    })
    .catch((err) => console.log(err));
});

onMounted(() => {
  axios
    .get("http://localhost:4200/api/users/location-leaders", { withCredentials: true })
    .then((response) => {
      locationLeaders.value = response.data;
      console.log(locationLeaders.value);
    })
    .catch((err) => console.log(err));
});

const openEditDialog = (location) => {
  editDialog.value = true;
  locationToEdit.value = location;
};
const confirmEdit = () => {
  const updatedLocation = {
    location_name: locationToEdit.value.location_name,
    user_id_location_leader: newLocationLeaderID.value,
  }
  axios
    .put(`http://localhost:4200/api/locations/${locationToEdit.value.id}`, updatedLocation, {
      withCredentials: true,
    })
    .then(() => {
      const updatedLeader = locationLeaders.value.find(
        (leader) => leader.id === newLocationLeaderID.value
      );

      if (updatedLeader) {
        const locationIndex = locations.value.findIndex(
          (loc) => loc.id === locationToEdit.value.id
        );

        if (locationIndex !== -1) {
          locations.value[locationIndex].location_leader = updatedLeader;
        }
      }
      closeEditDialog();
      snackbarText.value = "Der Standort wurde erfolgreich aktualisiert!";
      snackbar.value = true;
    })
    .catch((err) => {
      console.error("Error updating location:", err);
    });
};
const closeEditDialog = () => {
  editDialog.value = false;
  locationToEdit.value = null;
  newLocationLeaderID.value = null;
  newLocationLeaderName.value = null;
  form.value = false;
};
const selectLeader = (newLeader) => {
  newLocationLeaderID.value = newLeader.id;
  newLocationLeaderName.value = newLeader.first_name+" "+newLeader.last_name;
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
  axios
    .delete(`http://localhost:4200/api/locations/${locationToDelete.value.id}`, {
      withCredentials: true,
    })
    .then(() => {
      locations.value = locations.value.filter(
        (location) => location.id !== locationToDelete.value.id
      );
      closeDeleteDialog();
      snackbarText.value = "Der Standort wurde erfolgreich gelöscht!";
      snackbar.value = true;
    })
    .catch((err) => console.log(err));
};

</script>
