<template>
  <v-data-table-virtual
    :headers="headers"
    :items="props.users"
    :sort-by="sortBy"
    :hover="true"
    item-value="id"
    class="my-2"
    style="width: 60%"
    :row-props="colorRowItem"
  >
    <template v-slot:[`item.username`]="{ item }">
      <span>{{ item.username }}</span>
      <span v-if="item.blocked" class="font-italic"> (gesperrt)</span>
    </template>

    <template v-slot:[`item.user_group`]="{ item }">
      <v-chip
        :class="item.blocked ? 'blockedBackground' : ''"
        :prepend-icon="
          item.user_group === 'verwaltung'
            ? 'mdi-shield-account'
            : 'mdi-badge-account'
        "
        :color="item.user_group === 'verwaltung' ? 'red' : 'primary'"
        density="comfortable"
      >
        {{ formattedRole(item.user_group) }}
      </v-chip>
    </template>
    <template v-slot:[`item.actions`]="{ item }">
      <v-btn
        icon="mdi-lead-pencil"
        class="bg-primary mr-2"
        @click="openeditDialog(item), (hasChanged = false)"
        size="small"
      ></v-btn>
      <v-btn
        icon="mdi-trash-can-outline"
        class="bg-red"
        @click="opendeleteDialog(item)"
        size="small"
      ></v-btn>
    </template>
  </v-data-table-virtual>

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
            <strong>{{ props.firstName + " " + props.lastName }}</strong>
            löschen möchten?
          </p>
        </div>
      </v-card-text>
      <v-card-actions>
        <v-btn text @click="deleteDialog = false">Abbrechen</v-btn>
        <v-btn color="red" variant="elevated" @click="confirmDelete"
          >Löschen</v-btn
        >
      </v-card-actions>
    </v-card>
  </v-dialog>
  <v-dialog v-model="editDialog" no-click-animation persistent max-width="500">
    <v-card>
      <v-card-text>
        <div class="d-flex ga-3 ms-2 mb-5 mt-2 text-primary">
          <div class="d-flex align-center">
            <v-icon size="x-large">mdi-account-edit</v-icon>
          </div>
          <h2>Benutzer bearbeiten</h2>
        </div>

        <div>
          <v-form ref="validation" v-model="form">
            <v-radio-group
              v-model="user_group"
              @update:model-value="hasChanged = true"
              :rules="[required]"
              color="primary"
            >
              <div class="d-flex">
                <v-radio
                  base-color="blue-grey"
                  label="Verwaltung"
                  value="verwaltung"
                >
                  <template v-slot:label="{ label }">
                    <span class="text-blue-grey-darken-4">{{ label }} </span>
                  </template>
                </v-radio>
                <v-radio
                  base-color="blue-grey"
                  label="Standortleitung"
                  value="standortleitung"
                >
                  <template v-slot:label="{ label }">
                    <span class="text-blue-grey-darken-4">{{ label }} </span>
                  </template></v-radio
                >
              </div>
              <div class="d-flex">
                <v-radio
                  base-color="blue-grey"
                  label="Gruppenleitung"
                  value="gruppenleitung"
                >
                  <template v-slot:label="{ label }">
                    <span class="text-blue-grey-darken-4">{{ label }} </span>
                  </template></v-radio
                >
                <v-radio
                  base-color="blue-grey"
                  label="Küchenpersonal"
                  value="kuechenpersonal"
                >
                  <template v-slot:label="{ label }">
                    <span class="text-blue-grey-darken-4">{{ label }} </span>
                  </template></v-radio
                >
              </div>
            </v-radio-group>
            <div class="d-flex ga-5">
              <v-text-field
                v-model="first_name"
                :rules="[required]"
                @update:model-value="hasChanged = true"
                base-color="blue-grey"
                color="primary"
                variant="outlined"
                class="mb-2"
                label="Vorname"
                clearable
              ></v-text-field>
              <v-text-field
                v-model="last_name"
                @update:model-value="hasChanged = true"
                base-color="blue-grey"
                color="primary"
                variant="outlined"
                :rules="[required]"
                class="mb-2"
                label="Nachname"
                clearable
              ></v-text-field>
            </div>
            <div block>
              <v-text-field
                base-color="blue-grey"
                @update:model-value="hasChanged = true"
                color="primary"
                variant="outlined"
                class="mb-2"
                v-model="username"
                :rules="[required]"
                label="Benutzername"
                clearable
              ></v-text-field>
              <div></div>
            </div>
            <v-btn
              @click="handlePasswordReset"
              class="bg-primary mb-3 mt-4"
              block
              >Passwort zurücksetzen</v-btn
            >
            <v-btn
              v-if="userToEditID != appStore.userData.id"
              class="bg-blue-grey w-100 mt-4 mb-2"
              block
              @click="blocking(userToEditID)"
              >{{
                isBlocked ? "Benutzer entsperren" : "Benutzer sperren"
              }}</v-btn
            >
          </v-form>
        </div>
      </v-card-text>
      <v-card-actions class="mb-2" :class="!hasChanged ? 'me-2' : ''">
        <v-btn text @click="editDialog = false">{{
          hasChanged ? "Verwerfen" : "Zurück"
        }}</v-btn>
        <v-btn
          v-if="hasChanged"
          color="primary"
          class="me-4"
          :disabled="!form"
          type="submit"
          variant="elevated"
          @click="confirmEdit"
          >Übernehmen</v-btn
        >
      </v-card-actions>
    </v-card>
    <ConfirmDialogCreateUser
      :showConfirm="showConfirm"
      :user-name="username"
      user-group=""
      :initial-password="initialPassword"
      text="Das Passwort wurde erfolgreich zurückgesetzt"
      @close="showConfirm = false"
    />
  </v-dialog>
  <SuccessSnackbar v-model="snackbar" :text="snackbarText"></SuccessSnackbar>
  <ErrorSnackbar
    v-model="errorSnackbar"
    :text="errorSnackbarText"
  ></ErrorSnackbar>
</template>

<script setup>
import axios from "axios";
import { useAppStore } from "@/stores/app";
const appStore = useAppStore();

const props = defineProps(["users"]);
const emit = defineEmits(["user-removed", "user-edited"]);

const headers = [
  {
    title: "Benutzername",
    key: "username",
    nowrap: true,
  },
  {
    title: "Gesperrt",
    key: "blocked",
    nowrap: true,
    align: " d-none",
  },
  { title: "Vorname", key: "first_name", nowrap: true },
  { title: "Nachname", key: "last_name", nowrap: true },
  { title: "Rolle", key: "user_group", nowrap: true },
  { title: "", key: "actions", sortable: false, nowrap: true },
];
const sortBy = [{ key: "username", order: "asc" }];

const deleteDialog = ref(false);
const editDialog = ref(false);
const userToDeleteID = ref("");
const userToDelete = ref("");

const formattedRole = (role) => {
  let capitalized = role.charAt(0).toUpperCase() + role.slice(1);
  return capitalized.replace("ue", "ü");
};

const opendeleteDialog = (item) => {
  userToDelete.value = item.first_name + " " + item.last_name;
  userToDeleteID.value = item.id;
  deleteDialog.value = true;
};

const confirmDelete = () => {
  axios
    .delete(`${import.meta.env.VITE_API}/api/users/${userToDeleteID.value}`, {
      withCredentials: true,
    })
    .then(() => {
      emit("user-removed");
      deleteDialog.value = false;
      snackbarText.value = "Der Benutzer wurde erfolgreich gelöscht!";
      snackbar.value = true;
      employeeToDeleteID.value = " ";
    })
    .catch((err) => console.log(err));
};

const validation = ref("");
const form = ref(false);
const first_name = ref("");
const last_name = ref("");
const username = ref("");
const user_group = ref("");
const location_id = ref("");
const userToEditID = ref("");
const showConfirm = ref(false);
const initialPassword = ref();
const snackbarText = ref(" ");
const snackbar = ref(false);
const errorSnackbar = ref(false);
const errorSnackbarText = ref(" ");
const isBlocked = ref(false);
const hasChanged = ref(false);

const handlePasswordReset = () => {
  axios
    .put(
      `${import.meta.env.VITE_API}/api/users/${
        userToEditID.value
      }/reset-password`,
      {},
      { withCredentials: true }
    )
    .then((response) => {
      initialPassword.value = response.data.new_password;
      showConfirm.value = true;
    })
    .catch((err) => {
      console.log(err);
    });
};

const required = (v) => {
  return !!v || "Eingabe erforderlich";
};

const openeditDialog = (item) => {
  isBlocked.value = item.blocked;
  userToEditID.value = item.id;
  first_name.value = item.first_name;
  last_name.value = item.last_name;
  username.value = item.username;
  user_group.value = item.user_group;
  location_id.value = item.location_id;
  editDialog.value = true;
};

const confirmEdit = () => {
  const updatedUser = {
    first_name: first_name.value,
    last_name: last_name.value,
    username: username.value,
    user_group: user_group.value,
    location_id: location_id.value,
  };

  axios
    .put(
      import.meta.env.VITE_API + `/api/users/${userToEditID.value}`,
      updatedUser,
      {
        withCredentials: true,
      }
    )
    .then(() => {
      emit("user-edited");
      editDialog.value = false;
      snackbarText.value = "Der Benutzer wurde erfolgreich aktualisiert!";
      snackbar.value = true;
    })
    .catch((err) => {
      console.error("Error updating user:", err);
    });
};
function colorRowItem({ item }) {
  if (item.blocked) {
    console.log("TEST");
    return { class: "text-blue-grey" };
  }
}

const blocking = (userToEditID) => {
  if (!isBlocked.value) {
    axios
      .put(
        import.meta.env.VITE_API + `/api/users/${userToEditID}/block`,
        {},
        {
          withCredentials: true,
        }
      )
      .then((response) => {
        console.log(response.data);
        isBlocked.value = !isBlocked.value;
        snackbarText.value = response.data.message + "!";
        snackbar.value = true;
        emit("user-edited");
      })
      .catch((err) => {
        errorSnackbarText.value = err.message;
        errorSnackbar.value = true;
      });
  } else {
    axios
      .put(
        import.meta.env.VITE_API + `/api/users/${userToEditID}/unblock`,
        {},
        {
          withCredentials: true,
        }
      )
      .then((response) => {
        console.log(response.data);
        isBlocked.value = !isBlocked.value;
        snackbarText.value = response.data.message + "!";
        snackbar.value = true;
        emit("user-edited");
      })
      .catch((err) => {
        errorSnackbarText.value = err.message;
        errorSnackbar.value = true;
      });
  }
};
if (isBlocked) {
  isBlocked.value = true;
}
</script>

<style scoped>
.blockedBackground {
  background-image: linear-gradient(
    135deg,
    #eceff1 25%,
    #ffffff00 25%,
    #ffffff00 50%,
    #eceff1 50%,
    #eceff1 75%,
    #ffffff00 75%,
    #ffffff00 100%
  );
  background-size: 25px 25px;
}
</style>
