<template>
  <NavbarVerwaltung />
  <div class="mx-4 my-5 d-flex justify-start flex-wrap">
    <UserCard
      v-for="user in users"
      :id="user.id"
      :name="user.username"
      :role="user.user_group"
      @delete="openDialog"
    />
  </div>
  <v-dialog v-model="deleteConfirmation" persistent max-width="400">
    <v-card>
      <v-card-title class="text-error d-flex justify-start">
        <v-icon left class="mr-2">
            mdi-alert-circle-outline
        </v-icon>
        <span class="text-h5">Löschanfrage</span>
      </v-card-title>
      <v-card-text>
        Sind Sie sicher, dass Sie den Benutzer 
        <strong>{{ userToDeleteName }}</strong> löschen möchten?
      </v-card-text>
      <v-card-actions>
        <v-btn text @click="closeDialog">Abbrechen</v-btn>
        <v-btn color="error" text @click="confirmDelete">Löschen</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
  <SuccessSnackbar v-model="snackbar" :text="snackbarText" @close="snackbar = false"></SuccessSnackbar>
</template>

<script setup>
import axios from "axios";
const snackbarText = ref("Der Benutzer wurde erfolgreich gelöscht!");
const snackbar = ref(false);
const users = ref({});
const deleteConfirmation = ref(false);
const userToDelete = ref(null);
const userToDeleteName = ref("");

onMounted(() => {
  axios
    .get("http://localhost:4200/api/users", { withCredentials: true })
    .then((response) => {
      users.value = response.data;
      console.log(users.value);
    })
    .catch((err) => console.log(err));
});

const openDialog = (id) => {
  const user = users.value.find((user) => user.id === id);
  userToDelete.value = id;
  userToDeleteName.value = user?.username;
  deleteConfirmation.value = true;
};

const closeDialog = () => {
  deleteConfirmation.value = false;
  userToDelete.value = null;
};

const confirmDelete = () => {
  axios
    .delete(`http://localhost:4200/api/users/${userToDelete.value}`, {
      withCredentials: true,
    })
    .then(() => {
      users.value = users.value.filter((user) => user.id !== userToDelete.value);
      closeDialog();
      snackbar.value = true;
    })
    .catch((err) => console.log(err));
};

</script>
