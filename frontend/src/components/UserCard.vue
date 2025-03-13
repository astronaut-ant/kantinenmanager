<template>
  <v-card
    class="mx-2 my-2 text-blue-grey-darken-2"
    width="425"
    elevation="16"
    :class="isBlocked ? 'blockedBackground' : ''"
  >
    <v-card-item>
      <div class="d-flex align-center">
        <div>
          <v-avatar :color="color" size="large" class="pa-6">
            <span class="text-h5">{{
              props.firstName.charAt(0) + props.lastName.charAt(0)
            }}</span>
          </v-avatar>
        </div>
        <div class="ml-4">
          <v-card-title>
            {{ props.firstName + " " + props.lastName }}
          </v-card-title>
          <v-card-subtitle>
            <v-icon :color="color" icon="mdi-at" size="small"></v-icon>
            <span class="me-1 ml-1"> {{ props.username }} </span>
            <span v-if="isBlocked" class="font-italic">(gesperrt)</span>
          </v-card-subtitle>
        </div>
      </div>
    </v-card-item>
    <v-card-text>
      <v-divider></v-divider>
      <div class="mt-3 d-flex justify-space-between align-center">
        <v-chip
          :prepend-icon="isOwnCard ? 'mdi-shield-account' : 'mdi-badge-account'"
          :color="color"
          density="comfortable"
        >
          {{ formattedRole }}
        </v-chip>
        <div class="d-flex ga-1 justify-end">
          <v-btn
            class="bg-primary"
            @click="(editDialog = true), (hasChanged = false)"
            size="default"
            density="comfortable"
            ><v-icon>mdi-lead-pencil</v-icon></v-btn
          >
          <v-btn
            class="bg-red"
            @click="deleteDialog = true"
            :disabled="isOwnCard || props.isFixed"
            size="default"
            density="comfortable"
            ><v-icon>mdi-trash-can-outline</v-icon></v-btn
          >
        </div>
      </div>
    </v-card-text>
  </v-card>
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
  <v-dialog v-model="editDialog" no-click-animation persistent max-width="600">
    <v-card>
      <v-card-text>
        <div class="d-flex ga-3 mb-4 text-primary">
          <div class="d-flex align-center">
            <v-icon class="mt-n1" size="35">mdi-account-edit</v-icon>
          </div>
          <h1>Benutzer bearbeiten</h1>
        </div>

        <div>
          <v-form ref="validation" v-model="form">
            <v-radio-group
              :disabled="isOwnCard || props.isFixed"
              v-model="user_group"
              @update:model-value="hasChanged = true"
              :rules="[required]"
              color="primary"
            >
              <div class="d-flex">
                <v-radio
                  class="ms-n2"
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
                  class="ms-n2"
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
              class="bg-blue-grey w-100 mt-4 mb-2"
              :disabled="isOwnCard"
              block
              @click="blocking"
              >{{
                isBlocked ? "Benutzer entsperren" : "Benutzer sperren"
              }}</v-btn
            >
          </v-form>
        </div>
      </v-card-text>
      <v-card-actions class="mb-2" :class="!hasChanged ? 'me-4' : ''">
        <v-btn
          text
          color="blue-grey"
          @click="(editDialog = false), restore()"
          >{{ hasChanged ? "Abbrechen" : "Zurück" }}</v-btn
        >
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

const props = defineProps([
  "id",
  "blocked",
  "username",
  "role",
  "firstName",
  "lastName",
  "location_id",
  "isFixed",
]);
const emit = defineEmits(["user-removed", "user-edited", "avatar-changed"]);
const color = ref("primary");
const deleteDialog = ref(false);
const editDialog = ref(false);

const formattedRole = computed(() => {
  let capitalized = props.role.charAt(0).toUpperCase() + props.role.slice(1);
  return capitalized.replace("ue", "ü");
});

const confirmDelete = () => {
  axios
    .delete(`${import.meta.env.VITE_API}/api/users/${props.id}`, {
      withCredentials: true,
    })
    .then(() => {
      emit("user-removed");
      deleteDialog.value = false;
      snackbarText.value = "Der Benutzer wurde erfolgreich gelöscht!";
      snackbar.value = true;
    })
    .catch((err) => {
      console.log(err);
      errorSnackbarText.value = "Fehler beim löschen des Nutzers!";
      errorSnackbar.value = true;
    });
};

const validation = ref("");
const form = ref(false);
const first_name = ref(props.firstName);
const last_name = ref(props.lastName);
const username = ref(props.username);
const user_group = ref(props.role);
const showConfirm = ref(false);
const initialPassword = ref();
const snackbarText = ref(" ");
const snackbar = ref(false);
const errorSnackbar = ref(false);
const errorSnackbarText = ref(" ");
const isBlocked = ref(false);
const hasChanged = ref(false);
const isOwnCard = ref(false);
const handlePasswordReset = () => {
  axios
    .put(
      `${import.meta.env.VITE_API}/api/users/${props.id}/reset-password`,
      {},
      { withCredentials: true }
    )
    .then((response) => {
      initialPassword.value = response.data.new_password;
      showConfirm.value = true;
    })
    .catch((err) => {
      console.log(err);
      errorSnackbarText.value = "Fehler beim zurücksetzen des Passwortes!";
      errorSnackbar.value = true;
    });
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

  console.log(updatedUser);
  axios
    .put(import.meta.env.VITE_API + `/api/users/${props.id}`, updatedUser, {
      withCredentials: true,
    })
    .then(() => {
      emit("user-edited");
      editDialog.value = false;
      snackbarText.value = "Der Benutzer wurde erfolgreich aktualisiert!";
      snackbar.value = true;
      if (isOwnCard.value) {
        appStore.userData.first_name = first_name.value;
        appStore.userData.last_name = last_name.value;
        appStore.userData.username = username.value;
        emit("avatar-changed");
      }
    })
    .catch((err) => {
      console.error("Error updating user:", err);
      errorSnackbarText.value = "Fehler beim aktualisieren des Benutzers!";
      errorSnackbar.value = true;
    });
};

const blocking = () => {
  if (!isBlocked.value) {
    axios
      .put(
        import.meta.env.VITE_API + `/api/users/${props.id}/block`,
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
      })
      .catch((err) => {
        errorSnackbarText.value = err.message;
        errorSnackbar.value = true;
      });
  } else {
    axios
      .put(
        import.meta.env.VITE_API + `/api/users/${props.id}/unblock`,
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
      })
      .catch((err) => {
        errorSnackbarText.value = err.message;
        errorSnackbar.value = true;
      });
  }
};
if (props.blocked) {
  isBlocked.value = true;
}
const restore = () => {
  setTimeout(() => {
    first_name.value = props.firstName;
    last_name.value = props.lastName;
    username.value = props.username;
    user_group.value = props.role;
  }, 500);
};

if (appStore.userData.id === props.id) {
  isOwnCard.value = true;
  color.value = "red";
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
  background-size: 56.57px 56.57px;
}
</style>
