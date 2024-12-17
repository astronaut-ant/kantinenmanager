<template>
  <NavbarVerwaltung />
  <div class="mx-4 my-5 d-flex justify-start flex-wrap">
    <UserCard
      v-for="user in users"
      :id="user.id"
      :name="user.username"
      :role="user.user_group"
      :firstName="user.first_name"
      :lastName="user.last_name"
      @delete="opendeleteDialog"
      @edit="openeditDialog"
    />
  </div>
  <v-dialog
    v-model="deleteDialog"
    no-click-animation
    persistent
    max-width="400"
  >
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

  <v-dialog v-model="editDialog" no-click-animation persistent max-width="500">
    <v-card>
      <v-card-text>
        <div class="d-flex justify-center align-center text-primary mb-7">
          <p class="text-h5 font-weight-black">Benutzer bearbeiten</p>
        </div>
        <div>
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
                <v-radio
                  label="Gruppenleitung"
                  value="gruppenleitung"
                ></v-radio>
                <v-radio
                  label="Küchenpersonal"
                  value="kuechenpersonal"
                ></v-radio>
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
            <div block>
              <v-text-field
                v-model="username"
                :rules="[required]"
                label="Benutzername"
                clearable
              ></v-text-field>
              <div>
                <v-select
                  class="mb-2"
                  v-if="user_group === 'kuechenpersonal'"
                  v-model="locationName"
                  :items="allLocations"
                  :rules="[required]"
                  label="Standort"
                ></v-select>
              </div>
            </div>
            <v-btn @click="handlePasswordReset" class="bg-red" block
              >Passwort zurücksetzen</v-btn
            >
          </v-form>
        </div>
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
    <ConfirmDialogCreateUser
      :showConfirm="showConfirm"
      :user-name="username"
      user-group=""
      :initial-password="initialPassword"
      text="Das Passwort wurder erfolgreich zurückgesetzt"
      @close="showConfirm = false"
    />
  </v-dialog>
  <SuccessSnackbar
    v-model="snackbar"
    :text="snackbarText"
    @close="snackbar = false"
  ></SuccessSnackbar>
</template>

<script setup>
import ConfirmDialogCreateUser from "@/components/ConfirmDialogCreateUser.vue";
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
const showConfirm = ref(false);
const initialPassword = ref();
const allLocations = ref([]);
const location_id = ref("");
const locationName = ref("Test");
const locationMap = {};
const locationMapReversed = {};
onMounted(() => {
  axios
    .get(import.meta.env.VITE_API + "/api/users", { withCredentials: true })
    .then((response) => {
      users.value = response.data;
      console.log(users.value);
    })
    .catch((err) => console.log(err));

  axios
    .get(import.meta.env.VITE_API + "/api/locations", { withCredentials: true })
    .then((response) => {
      response.data.forEach((location) => {
        const name = location.location_name;
        const id = location.id;
        locationMap[id] = name;
        locationMapReversed[name] = id;
      });
      allLocations.value = Object.values(locationMap);
      console.log(locationMap);
    })
    .catch((err) => console.log(err.response.data.description));
});

const opendeleteDialog = (id) => {
  const user = users.value.find((user) => user.id === id);
  userToDelete.value = id;
  userToDeleteName.value =
    user?.first_name +
    " " +
    user?.last_name +
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
    .delete(`${import.meta.env.VITE_API}/api/users/${userToDelete.value}`, {
      withCredentials: true,
    })
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
  console.log("userLocationId", user.location_id);
  locationName.value = locationMap[user.location_id];
  console.log("LocationName:", locationName.value);
  userToEdit.value = id;
  first_name.value = user.first_name;
  last_name.value = user.last_name;
  username.value = user.username;
  user_group.value = user.user_group;
  editDialog.value = true;
};

const handlePasswordReset = () => {
  axios
    .put(
      //What happens if User is Logged in?
      `${import.meta.env.VITE_API}/api/users/${
        userToEdit.value
      }/reset-password`,
      {},
      { withCredentials: true }
    )
    .then((response) => {
      console.log(response.data.new_password);
      initialPassword.value = response.data.new_password;
      showConfirm.value = true;
    })
    .catch((err) => {
      console.log(err);
    });
  console.log();
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
    location_id: locationMapReversed[locationName.value],
  };

  axios
    .put(
      import.meta.env.VITE_API + `/api/users/${userToEdit.value}`,
      updatedUser,
      {
        withCredentials: true,
      }
    )
    .then((response) => {
      console.log(response.data);
      const index = users.value.findIndex((u) => u.id === userToEdit.value);
      if (index !== -1) {
        users.value[index] = { ...users.value[index], ...updatedUser };
      }
      console.log("DONE");
      closeeditDialog();
      snackbarText.value = "Der Benutzer wurde erfolgreich aktualisiert!";
      snackbar.value = true;
    })
    .catch((err) => {
      console.error("Error updating user:", err);
    });
};
</script>
