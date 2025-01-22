<template>
    <v-data-table-virtual
        :headers="headers"  
        :items="props.users" 
        :sort-by="sortBy" 
        :hover="true" 
        item-value="id"
        class="my-2"
        style="width:60%"
        >
        <template v-slot:[`item.user_group`]="{ item }">
            <v-chip 
                :prepend-icon="item.user_group === 'verwaltung' ? 'mdi-shield-account' : 'mdi-badge-account'" 
                :color="item.user_group === 'verwaltung' ? 'red' : 'primary'"
                density="comfortable">
                {{ formattedRole(item.user_group) }}
            </v-chip>
        </template>
        <template v-slot:[`item.actions`]="{ item }">
            <v-btn icon="mdi-lead-pencil" class="bg-primary mr-2" @click="openeditDialog(item)" size="small"></v-btn>
            <v-btn icon="mdi-trash-can-outline" class="bg-red" @click="opendeleteDialog(item)" size="small"></v-btn>
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
                <strong> {{ userToDelete }} </strong> löschen möchten?
            </p>
            </div>
        </v-card-text>
        <v-card-actions>
            <v-btn text @click="deleteDialog = false">Abbrechen</v-btn>
            <v-btn color="red" variant="elevated" @click="confirmDelete"
            >Löschen</v-btn>
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
                        <v-radio-group v-model="user_group" :rules="[required]" color="primary">
                            <div class="d-flex">
                                <v-radio label="Verwaltung" value="verwaltung"></v-radio>
                                <v-radio label="Standortleitung" value="standortleitung"></v-radio>
                            </div>
                            <div class="d-flex">
                                <v-radio label="Gruppenleitung" value="gruppenleitung"></v-radio>
                                <v-radio label="Küchenpersonal" value="kuechenpersonal"></v-radio>
                            </div>
                        </v-radio-group>
                        <div class="d-flex ga-5">
                            <v-text-field v-model="first_name" :rules="[required]" class="mb-2" label="Vorname" clearable></v-text-field>
                            <v-text-field v-model="last_name" :rules="[required]" class="mb-2" label="Nachname" clearable></v-text-field>
                        </div>
                        <div block>
                            <v-text-field v-model="username" :rules="[required]" label="Benutzername" clearable></v-text-field>
                            <div></div>
                        </div>
                        <v-btn @click="handlePasswordReset" class="bg-red" block>Passwort zurücksetzen</v-btn>
                    </v-form>
                </div>
            </v-card-text>
            <v-card-actions>
                <v-btn text @click="editDialog = false">Abbrechen</v-btn>
                <v-btn color="primary" :disabled="!form" type="submit" variant="elevated" @click="confirmEdit">Speichern</v-btn>
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
</template>

<script setup>
import axios from "axios";
const props = defineProps(["users"]);
const emit = defineEmits(["user-removed", "user-edited"]);


const headers = [
     { title: "Benutzername", key: "username", nowrap: true },
     { title: "Vorname", key: "first_name", nowrap: true },
     { title: "Nachname", key: "last_name", nowrap: true },
     { title: "Rolle", key: "user_group", nowrap: true },
     { title: "", key: "actions", sortable: false, nowrap: true },];
const sortBy = [{ key: 'username', order: 'asc' }]

const deleteDialog = ref(false);
const editDialog = ref(false);
const userToDeleteID = ref("");
const userToDelete = ref("");

const formattedRole = (role) => {
    let capitalized = role.charAt(0).toUpperCase() + role.slice(1);
    return capitalized.replace("ue", "ü");
};

const opendeleteDialog = (item) => {
    userToDelete.value = item.first_name  + " " + item.last_name;
    userToDeleteID.value = item.id;
    deleteDialog.value= true;
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

const handlePasswordReset = () => {
    axios
        .put(
            `${import.meta.env.VITE_API}/api/users/${userToEditID.value}/reset-password`,
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
        location_id: location_id.value
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


</script>