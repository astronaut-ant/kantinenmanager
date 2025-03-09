<template>
    <v-card class="mx-2 my-2" width="425" elevation="16">
        <v-card-item>
            <v-card-title>{{ location_name }}</v-card-title>
            <v-card-subtitle>
                <v-icon color="primary" icon="mdi-account-circle" size="small"></v-icon>
                <span class="me-1 ml-2">{{ props.location_leader.first_name }} {{ props.location_leader.last_name }}</span>
            </v-card-subtitle>
            <li v-for="group in groups">{{ group }}</li>
        </v-card-item>
        <v-card-text>
            <v-divider></v-divider>
            <div class="mt-3 d-flex justify-space-between align-center">
                <v-chip prepend-icon="mdi-account-multiple" color="primary" label density="comfortable"> Gruppenanzahl: {{props.groups.length}} </v-chip>
                <div class="d-flex ga-1 justify-end">
                    <v-btn class="bg-primary mx-1" @click="openEditDialog" size="default" density="comfortable"><v-icon>mdi-lead-pencil</v-icon></v-btn>
                    <v-btn class="bg-red" @click="openDeleteDialog" size="default" density="comfortable"><v-icon>mdi-trash-can-outline</v-icon></v-btn>
                </div>
            </div>
        </v-card-text>
    </v-card>

    <v-dialog v-model="deleteDialog" persistent max-width="500">
    <v-card>
      <v-card-text>
        <div class="d-flex justify-center text-red mb-4">
          <p class="text-h5 font-weight-black">Standort löschen</p>
        </div>
        <div class="text-medium-emphasis">
          <p>
            Sind Sie sicher, dass Sie den Standort
            <strong>{{ props.location_name }}</strong> löschen
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

  <v-dialog v-model="secondDeleteDialog" persistent max-width="500">
    <v-card>
      <v-card-title class="text-red"
        >Standort kann nicht gelöscht werden</v-card-title
      >
      <v-card-text>
        <p>
          Der Standort
          <strong>{{ props.location_name }}</strong> enthält noch folgende Gruppen:
          <li class="mt-2 mb-2" v-for="group in groups">{{ group }}</li>
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

  <v-dialog v-model="editDialog" persistent>
    <LocationChange
      @close="closeEditDialog"
      @save="confirmEdit"
      @success="snackbarConfirm"
      @error="snackbarError"
      :oldValues="props"
    />
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
import axios from "axios";
const props = defineProps(["id", "location_name", "location_leader", "groups" ]);
const emit = defineEmits(["user-edited", "user-removed"]);

const deleteDialog = ref(false);
const secondDeleteDialog = ref(false);
const editDialog = ref(false);
const snackbar = ref(false);
const snackbarText = ref("");
const errorSnackbar = ref(false);
const errorSnackbarText = ("");

const openDeleteDialog = () => {
  deleteDialog.value = true;
};

const closeDeleteDialog = () => {
  deleteDialog.value = false;
  secondDeleteDialog.value = false;
};

const confirmDelete = () => {
  axios
    .delete(
      import.meta.env.VITE_API + `/api/locations/${props.id}`,
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

const openEditDialog = () => {
  editDialog.value = true;
};

const confirmEdit = () => {
    emit("user-edited");
    editDialog.value = false;
}

const closeEditDialog = () => {
    editDialog.value = false;
}; 

const snackbarConfirm = () => {
  snackbarText.value = "Der Standort wurde erfolgreich aktualisiert";
  snackbar.value = true;
};
const snackbarError = () => {
  errorSnackbarText.value = "Fehler beim aktualisieren des Standorts!"
  errorSnackbar.value = true;
}



</script>