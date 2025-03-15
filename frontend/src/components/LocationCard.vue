<template>
  <v-card class="mx-2 my-2 text-blue-grey-darken-2" width="425" elevation="16">
    <v-card-item>
      <div class="d-flex mb-2 justify-space-between align-center">
        <div>
          <v-card-title class="mb-2">{{ location_name }}</v-card-title>
          <v-card-subtitle>
            <v-icon
              color="primary"
              icon="mdi-account-circle"
              size="small"
            ></v-icon>
            <span class="me-1 ml-2"
              >{{ props.location_leader.first_name }}
              {{ props.location_leader.last_name }}</span
            >
          </v-card-subtitle>
        </div>
        <div class="d-flex align-center justify-end"></div>
      </div>
      <v-divider class="mb-3"></v-divider>
      <v-card-subtitle class="mb-2 mt-3">
        <v-icon
          class="mt-n1"
          color="primary"
          icon="mdi-account-group"
          size="small"
        ></v-icon>
        <span class="me-1 ml-2">Gruppen ({{ props.groups.length }}) </span>
      </v-card-subtitle>
      <v-sheet class="rounded-lg bg-white mt-1 mb-1 ms-n2">
        <v-slide-group
          v-if="props.groups.length > 0"
          show-arrows="always"
          class="flex-grow-1"
          :mobile="false"
        >
          <v-slide-group-item v-for="group in groups">
            <v-chip color="primary" class="mr-2" size="small">
              {{ group }}
            </v-chip>
          </v-slide-group-item>
        </v-slide-group>
        <v-chip
          v-if="props.groups.length === 0"
          color="blue-grey"
          class="ms-2"
          size="small"
          label
          append-icon="mdi-arrow-right-thin-circle-outline"
          :to="'/verwaltung/gruppen/neueGruppe'"
        >
          Gruppe anlegen
        </v-chip>
      </v-sheet>

      <v-divider class="mb-3 mt-3"></v-divider>
      <v-card-subtitle class="mb-2 mt-3">
        <v-icon
          class="mt-n1"
          color="primary"
          icon="mdi-chef-hat"
          size="small"
        ></v-icon>
        <span class="me-1 ml-2"
          >Küchenpersonal ({{ props.kitchen.length }})
        </span>
      </v-card-subtitle>
      <v-sheet class="rounded-lg bg-white mt-1 mb-1 ms-n2">
        <v-slide-group
          v-if="props.kitchen.length > 0"
          show-arrows="always"
          class="flex-grow-1"
          :mobile="false"
        >
          <v-slide-group-item v-for="ks in props.kitchen">
            <v-chip color="primary" class="mr-2" size="small">
              {{ ks.first_name }} {{ ks.last_name }}
            </v-chip>
          </v-slide-group-item>
        </v-slide-group>
        <v-chip
          v-if="props.kitchen.length === 0"
          color="blue-grey"
          class="ms-2"
          size="small"
          label
          append-icon="mdi-arrow-right-thin-circle-outline"
          @click="openEditDialog"
        >
          Küchenpersonal hinzufügen
        </v-chip>
      </v-sheet>
      <v-divider class="mt-3"></v-divider>
    </v-card-item>
    <v-card-actions class="justify-end me-2 mt-n1">
      <v-btn
        class="bg-primary mx-1"
        @click="openEditDialog"
        size="default"
        density="comfortable"
        ><v-icon>mdi-lead-pencil</v-icon></v-btn
      >
      <v-btn
        class="bg-red"
        @click="openDeleteDialog"
        size="default"
        density="comfortable"
        ><v-icon>mdi-trash-can-outline</v-icon></v-btn
      >
    </v-card-actions>
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
            <strong>{{ props.location_name }}</strong> löschen möchten?
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

  <v-dialog v-model="editDialog" persistent>
    <LocationChange
      @close="closeEditDialog"
      @save="confirmEdit"
      @success="FeedbackConfirm"
      @error="FeedbackError"
      :oldValues="props"
    />
  </v-dialog>
</template>

<script setup>
import axios from "axios";
import { useFeedbackStore } from "@/stores/feedback";
const feedbackStore = useFeedbackStore();

const props = defineProps([
  "id",
  "location_name",
  "location_leader",
  "groups",
  "kitchen",
]);
const emit = defineEmits(["location-edited", "location-removed"]);

const deleteDialog = ref(false);
const editDialog = ref(false);

const openDeleteDialog = () => {
  deleteDialog.value = true;
};

const closeDeleteDialog = () => {
  deleteDialog.value = false;
};

const confirmDelete = () => {
  axios
    .delete(import.meta.env.VITE_API + `/api/locations/${props.id}`, {
      withCredentials: true,
    })
    .then(() => {
      emit("location-removed");
      closeDeleteDialog();
      feedbackStore.setFeedback("success", "snackbar", "Standort gelöscht", `Der Standort ${props.location_name} wurde erfolgreich gelöscht!`);
    })
    .catch((err) => {
      console.log(err);
      deleteDialog.value = false;
      feedbackStore.setFeedback("error", "snackbar", err.response?.data?.title, err.response?.data?.description);
    });
};

const openEditDialog = () => {
  editDialog.value = true;
};

const confirmEdit = () => {
  emit("location-edited");
  editDialog.value = false;
};

const closeEditDialog = () => {
  editDialog.value = false;
};

const FeedbackConfirm = () => {
  feedbackStore.setFeedback("success", "snackbar", "", "Der Standort wurde erfolgreich aktualisiert");
};
const FeedbackError = () => {
  feedbackStore.setFeedback("error", "snackbar", "", "Fehler beim aktualisieren des Standorts!");
};
</script>

<style>
.v-slide-group__prev,
.v-slide-group__next {
  min-width: 30px;
  max-width: 30px;
}
</style>
