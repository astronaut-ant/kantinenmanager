<template>
    <v-card class="mx-2 my-2" width="425" elevation="16">
        <v-card-item>
            <div class="d-flex align-center">
                <div>
                    <v-avatar :color="color" size="large" class="pa-6">
                        <span class="text-h5">{{ props.firstName.charAt(0) + props.lastName.charAt(0) }}</span>
                    </v-avatar>
                </div>
                <div class="ml-4">
                    <v-card-title> 
                        {{ props.firstName + " " + props.lastName }}
                    </v-card-title>
                    <v-card-subtitle>
                        <v-icon
                            :color="color"
                            icon="mdi-at"
                            size="small"
                        ></v-icon>
                        <span class="me-1 ml-1"> {{ props.username }} </span>
                    </v-card-subtitle>
                </div>
            </div>
        </v-card-item>
        <v-card-text>
            <v-divider></v-divider>
            <div class="mt-3 d-flex justify-space-between align-center">
                <v-chip 
                    :prepend-icon="props.role === 'verwaltung' ? 'mdi-shield-account' : 'mdi-badge-account'" 
                    :color="color"
                    density="comfortable"
                    > {{ formattedRole }} </v-chip>
                <div class="d-flex ga-1 justify-end">
                    <v-btn class="bg-primary" @click="editDialog = true" size="default" density="comfortable"><v-icon>mdi-lead-pencil</v-icon></v-btn>
                    <v-btn class="bg-red" @click="deleteDialog = true" size="default" density="comfortable"><v-icon>mdi-trash-can-outline</v-icon></v-btn>
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
                <strong>{{ props.firstName + " " + props.lastName }}</strong> löschen möchten?
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
const props = defineProps(["id", "username", "role", "firstName", "lastName", "location_id"]);
const emit = defineEmits(["user-removed", "user-edited"]);
const color = computed(() => {
    switch (props.role) {
        case 'verwaltung':
            return 'red';
        default:
            return 'primary';
    }
});
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
    .catch((err) => console.log(err));
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
        location_id: props.location_id
    };

    axios
        .put(
            import.meta.env.VITE_API + `/api/users/${props.id}`,
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