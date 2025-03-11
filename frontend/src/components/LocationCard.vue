<template>
    <v-card class="mx-2 my-2" width="425" elevation="16">
        <v-card-item>
            <div class="d-flex mb-2 justify-space-between align-center">
              <div>
                <v-card-title>{{ location_name }}</v-card-title>
                <v-card-subtitle>
                  <v-icon color="primary" icon="mdi-account-circle" size="small"></v-icon>
                  <span class="me-1 ml-2">{{ props.location_leader.first_name }} {{ props.location_leader.last_name }}</span>
                </v-card-subtitle>
              </div>
              <div class="d-flex align-center justify-end">
                  <v-btn class="bg-primary mx-1" @click="openEditDialog" size="default" density="comfortable"><v-icon>mdi-lead-pencil</v-icon></v-btn>
                  <v-btn class="bg-red" @click="openDeleteDialog" size="default" density="comfortable"><v-icon>mdi-trash-can-outline</v-icon></v-btn>
              </div>
            </div>
            <v-divider class="mb-3"></v-divider>
            <v-card-subtitle class="mb-2 mt-3">
                <v-icon color="primary" icon="mdi-account-group" size="small"></v-icon>
                <span class="me-1 ml-2">{{ props.groups.length }} {{ props.groups.length === 1 ? 'Gruppe' : 'Gruppen' }}:</span>
            </v-card-subtitle>
            <v-sheet class="rounded-lg bg-white mt-1 mb-1">
              <v-slide-group class="flex-grow-1" :mobile="false" show-arrows="always">
                <v-slide-group-item v-for="group in groups" >
                    <v-chip
                        color="primary"
                        class="mr-2"
                        size="small"
                        >   
                        {{ group }}
                    </v-chip>
                </v-slide-group-item>
                <v-slide-group-item>
                    <v-chip color="grey-darken-1" class="mr-2" size="small" label append-icon="mdi-arrow-right-thin-circle-outline" :to="'/verwaltung/gruppen/neueGruppe'">
                      Gruppe anlegen
                  </v-chip>
                </v-slide-group-item>
              </v-slide-group>
            </v-sheet>
        </v-card-item>
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
      <v-card-text>
        <div class="d-flex justify-center text-red mb-4">
          <p class="text-h5 font-weight-black">Standort kann nicht gelöscht werden</p>
        </div>
        <div class="text-medium-emphasis">
          <p v-if="groups.length > 0">
          Der Standort
            <strong>{{ props.location_name }}</strong> enthält noch folgende Gruppen:
            <li class="mt-2 mb-2" v-for="group in groups">{{ group }}</li>
          </p>
          <p>
            Bitte löschen Sie zuerst alle Gruppen und Bestellungen, um den Standort zu löschen.
          </p>
        </div>
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
const emit = defineEmits(["location-edited", "location-removed"]);

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
    .then(() => {
      emit("location-removed");
      closeDeleteDialog();
      snackbarText.value = "Der Standort wurde erfolgreich gelöscht!";
      snackbar.value = true;
    })
    .catch((err) => {
      console.log(err);
      deleteDialog.value = false;
      secondDeleteDialog.value = true;
    });
};

const openEditDialog = () => {
  editDialog.value = true;
};

const confirmEdit = () => {
    emit("location-edited");
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

<style>
.v-slide-group__prev, .v-slide-group__next { min-width: 30px; max-width: 30px;}
</style>