<template>
  <NavbarVerwaltung />
  <div class="mx-4 my-5 d-flex justify-start flex-wrap">
    <UserCard
      v-for="user in users"
      :id="user.id"
      :name="user.username"
      :role="user.user_group"
      @delete="opendeleteDialog"
      @edit="openeditDialog"
    />
  </div>
  <v-dialog v-model="deleteDialog" persistent max-width="400">
    <v-card>
      <v-card-text>
        <div class="d-flex justify-center text-red mb-4">
          <p class="text-h5 font-weight-black">Benutzer löschen</p>
        </div>
        <div class="text-medium-emphasis">
          <p>
            Sind Sie sicher, dass Sie den Benutzer
            <strong>{{ userToDeleteName }}</strong> löschen möchten?
          </p>
        </div>
      </v-card-text>
      <v-card-actions>
        <v-btn text @click="closedeleteDialog">Abbrechen</v-btn>
        <v-btn color="red" variant="elevated" @click="confirmDelete"
          >Löschen</v-btn
        >
      </v-card-actions>
    </v-card>
  </v-dialog>

  <v-dialog v-model="editDialog" persistent max-width="400">
    <v-card>
      <v-card-title class="primary d-flex justify-start">
        <v-icon left class="mr-2"> mdi-account-edit-outline </v-icon>
        <span class="text-h5">Benutzer bearbeiten</span>
      </v-card-title>
      <v-card-text>
        <v-form ref="validation" v-model="form">
          <v-radio-group
            v-model="user_group"
            :rules="[required]"
            color="primary"
          >
            <div class="d-flex">
              <v-radio label="Verwaltung" value="verwaltung"></v-radio>
              <v-radio
                label="Standortleitung"
                value="standortleitung"
              ></v-radio>
            </div>
            <div class="d-flex">
              <v-radio label="Gruppenleitung" value="gruppenleitung"></v-radio>
              <v-radio label="Küchenpersonal" value="kuechenpersonal"></v-radio>
            </div>
          </v-radio-group>
          <div class="d-flex ga-5">
            <v-text-field
              v-model="first_name"
              :rules="[required]"
              class="mb-2"
              label="Vorname"
              clearable
            ></v-text-field>
            <v-text-field
              v-model="last_name"
              :rules="[required]"
              class="mb-2"
              label="Nachname"
              clearable
            ></v-text-field>
          </div>
          <div class="d-flex ga-5">
            <v-text-field
              v-model="username"
              :rules="[required]"
              label="Benutzername"
              clearable
            ></v-text-field>
          </div>
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-btn text @click="closeeditDialog">Abbrechen</v-btn>
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
  <SuccessSnackbar
    v-model="snackbar"
    :text="snackbarText"
    @close="snackbar = false"
  ></SuccessSnackbar>
</template>

<script setup>
import UserCard from "@/components/UserCard.vue";
import axios from "axios";
const snackbarText = ref(" ");
const snackbar = ref(false);
const users = ref({});
const deleteDialog = ref(false);
const editDialog = ref(false);
const userToEdit = ref(null);
const userToDelete = ref(null);
const userToDeleteName = ref("");

const validation = ref("");
const form = ref(false);
const first_name = ref("");
const last_name = ref("");
const username = ref("");
const user_group = ref("");

onMounted(() => {
  axios
    .get(import.meta.env.VITE_API + "/api/users", { withCredentials: true })
    .then((response) => {
      users.value = response.data;
      // console.log(users.value);
    })
    .catch((err) => console.log(err));
});

const opendeleteDialog = (id) => {
  const user = users.value.find((user) => user.id === id);
  userToDelete.value = id;
  userToDeleteName.value =
    user?.last_name +
    ", " +
    user?.first_name +
    " (Benutzername: " +
    user?.username +
    ")";
  deleteDialog.value = true;
};

const closedeleteDialog = () => {
  deleteDialog.value = false;
  userToDelete.value = null;
};

const confirmDelete = () => {
  axios
    .delete(
      import.meta.env.VITE_API +
        `http://localhost:4200/api/users/${userToDelete.value}`,
      {
        withCredentials: true,
      }
    )
    .then(() => {
      users.value = users.value.filter(
        (user) => user.id !== userToDelete.value
      );
      closedeleteDialog();
      snackbarText.value = "Der Benutzer wurde erfolgreich gelöscht!";
      snackbar.value = true;
    })
    .catch((err) => console.log(err));
};

const closeeditDialog = () => {
  editDialog.value = false;
  userToEdit.value = null;
};

const openeditDialog = (id) => {
  const user = users.value.find((user) => user.id === id);

  userToEdit.value = id;
  first_name.value = user.first_name;
  last_name.value = user.last_name;
  username.value = user.username;
  user_group.value = user.user_group;
  editDialog.value = true;
};

const required = (v) => {
  return !!v || "Eingabe erforderlich";
};

const confirmEdit = () => {
  const updatedUser = {
    first_name: first_name.value,
    last_name: last_name.value,
    username: username.value,
    user_group: user_group.value,
  };

  axios
    .put(
      import.meta.env.VITE_API + `/api/users/${userToEdit.value}`,
      updatedUser,
      {
        withCredentials: true,
      }
    )
    .then(() => {
      const index = users.value.findIndex((u) => u.id === userToEdit.value);
      if (index !== -1) {
        users.value[index] = { ...users.value[index], ...updatedUser };
      }
      closeeditDialog();
      snackbarText.value = "Der Benutzer wurde erfolgreich aktualisiert!";
      snackbar.value = true;
    })
    .catch((err) => {
      console.error("Error updating user:", err);
    });
};
</script>
