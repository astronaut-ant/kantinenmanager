<template>
  <NavbarVerwaltung />
  <div class="mx-4 my-5 d-flex justify-start flex-wrap">
    <v-card
      class="mx-4 my-4"
      elevation="16"
      min-width="20em"
      max-width="20em"
      v-for="location in locations"
      :key="location?.id"
    >
      <v-card-item>
        <v-card-title>
          <div class="d-flex flex-column">
            <span class="text-h6 font-weight-bold text-truncate">
              Standort: {{ location?.location_name }}
            </span>
            <span class="text-subtitle-2 text-truncate">
              Standortleiter:
              {{ location?.location_leader.first_name }}
              {{ location?.location_leader.last_name }}
            </span>
          </div>
        </v-card-title>
        <v-divider></v-divider>
        <v-card-actions class="justify-end">
          <v-btn class="mt-2 bg-primary" density="comfortable" @click="openEditDialog(location)">
            <v-icon>mdi-lead-pencil</v-icon>
          </v-btn>
          <v-btn class="mt-2 bg-red" density="comfortable" @click="handleDelete(location)">
            <v-icon>mdi-trash-can-outline</v-icon>
          </v-btn>
        </v-card-actions>
      </v-card-item>
    </v-card>
  </div>

  <v-dialog v-model="editDialog" persistent>
    <LocationChange
      @close="closeEditDialog"
      @save="initialize"
      @success="snackbarConfirm"
      @error="snackbarError"
      :oldValues="locationToEdit"
    />
  </v-dialog>

  <v-dialog v-model="deleteDialog" persistent max-width="600">
    <v-card>
      <v-card-text>
        <div class="d-flex justify-center text-red mb-4">
          <p class="text-h5 font-weight-black">Standort löschen</p>
        </div>
        <div class="text-medium-emphasis">
          <p>
            Sind Sie sicher, dass Sie den Standort
            <strong>{{ locationToDelete?.location_name }}</strong> löschen
            möchten?
          </p>
        </div>
      </v-card-text>
      <v-card-actions>
        <v-btn text @click="closeDeleteDialog">Abbrechen</v-btn>
        <v-btn color="red" variant="elevated" @click="confirmDelete"
          >Löschen</v-btn
        >
      </v-card-actions>
    </v-card>
  </v-dialog>

  <v-dialog v-model="secondDeleteDialog" persistent max-width="600">
    <v-card>
      <v-card-title class="text-red"
        >Standort kann nicht gelöscht werden</v-card-title
      >
      <v-card-text>
        <p>
          Der Standort
          <strong>{{ locationToDelete?.location_name }}</strong> enthält noch
          Gruppen.
        </p>
        <p>
          Bitte löschen Sie zuerst alle Gruppen, um den Standort zu löschen.
        </p>
      </v-card-text>
      <v-card-actions>
        <v-btn text @click="closeDeleteDialog">Schließen</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
  <SuccessSnackbar
    v-model="snackbar"
    :text="snackbarText"
    @close="snackbar = false"
  ></SuccessSnackbar>
  <ErrorSnackbar
    v-model="errorSnackbar"
    :text="errorSnackbarText"
    @close="errorSnackbar = false"
  ></ErrorSnackbar>
</template>

<script setup>
import LocationChange from "@/components/LocationChange.vue";
import LocationCreation from "@/components/LocationCreation.vue";
import axios from "axios";
const locations = ref({});
const locationLeaders = ref({});
const newLocationLeaderID = ref(null);
const newLocationLeaderName = ref("");
const form = ref(false);
const editDialog = ref(false);
const locationToEdit = ref(null);
const deleteDialog = ref(false);
const secondDeleteDialog = ref(false);
const locationToDelete = ref(null);
const snackbar = ref(false);
const snackbarText = ref("");
const errorSnackbar = ref(false);
const errorSnackbarText = ("");

const initialize = () => {
  axios
    .get(import.meta.env.VITE_API + "/api/locations", { withCredentials: true })
    .then((response) => {
      locations.value = response.data;
      // console.log(locations.value);
    })
    .catch((err) => {
      console.log(err);
      errorSnackbarText.value = "Fehler beim Laden der Standorte!";
      errorSnackbar.value = true;
    });
  axios
    .get(import.meta.env.VITE_API + "/api/users/location-leaders", {
      withCredentials: true,
    })
    .then((response) => {
      locationLeaders.value = response.data;
    })
    .catch((err) => console.log(err));
};

onMounted(() => {
  initialize();
});

const openEditDialog = (location) => {
  editDialog.value = true;
  locationToEdit.value = location;
};
// const confirmEdit = () => {
//   const updatedLocation = {
//     location_name: locationToEdit.value.location_name,
//     user_id_location_leader: newLocationLeaderID.value,
//   };

//   axios
//     .put(
//       import.meta.env.VITE_API + `/api/locations/${locationToEdit.value.id}`,
//       updatedLocation,
//       {
//         withCredentials: true,
//       }
//     )
//     .then(() => {
//       const oldLocationLeaderID = locationToEdit.value.location_leader?.id;
//       const oldLeaderIndex = locationLeaders.value.findIndex(
//         (leader) => leader.id === oldLocationLeaderID
//       );
//       if (oldLocationLeaderID) {
//         locationLeaders.value[oldLeaderIndex].leader_of_location = null;
//       }
//       const updatedLeader = locationLeaders.value.find(
//         (leader) => leader.id === newLocationLeaderID.value
//       );

//       if (updatedLeader) {
//         const locationIndex = locations.value.findIndex(
//           (loc) => loc.id === locationToEdit.value.id
//         );

//         if (locationIndex !== -1) {
//           locations.value[locationIndex].location_leader = updatedLeader;
//         }
//       }
//       const newLeaderIndex = locationLeaders.value.findIndex(
//         (leader) => leader.id === newLocationLeaderID.value
//       );
//       locationLeaders.value[newLeaderIndex].leader_of_location =
//         locationToEdit.value;
//       closeEditDialog();
//       snackbarText.value = "Der Standort wurde erfolgreich aktualisiert!";
//       snackbar.value = true;
//     })
//     .catch((err) => {
//       console.error("Error updating location:", err);
//     });
// };
const snackbarConfirm = () => {
  snackbarText.value = "Der Standort wurde erfolgreich aktualisiert";
  snackbar.value = true;
};
const snackbarError = () => {
  errorSnackbarText.value = "Fehler beim aktualisieren des Standorts!"
  errorSnackbar.value = true;
}
const closeEditDialog = () => {
  editDialog.value = false;
  locationToEdit.value = null;
  newLocationLeaderID.value = null;
  newLocationLeaderName.value = null;
  form.value = false;
};
const selectLeader = (newLeader) => {
  newLocationLeaderID.value = newLeader.id;
  newLocationLeaderName.value =
    newLeader.first_name + " " + newLeader.last_name;
  form.value = true;
};

const handleDelete = (location) => {
  locationToDelete.value = location;
  deleteDialog.value = true;
};
const closeDeleteDialog = () => {
  locationToDelete.value = null;
  deleteDialog.value = false;
  secondDeleteDialog.value = false;
};
const confirmDelete = () => {
  axios
    .delete(
      import.meta.env.VITE_API + `/api/locations/${locationToDelete.value.id}`,
      {
        withCredentials: true,
      }
    )
    .then((response) => {
      console.log(response.data);
      locations.value = locations.value.filter(
        (location) => location.id !== locationToDelete.value.id
      );
      closeDeleteDialog();
      snackbarText.value = "Der Standort wurde erfolgreich gelöscht!";
      snackbar.value = true;
    })
    .catch((err) => {
      console.log(err);
      secondDeleteDialog.value = true;
    });
};
</script>
