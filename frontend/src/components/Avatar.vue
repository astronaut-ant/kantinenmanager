<template>
  <v-container class="w-25 me-5" fluid>
    <v-row justify="end">
      <v-menu min-width="200px" rounded>
        <template v-slot:activator="{ props }">
          <v-btn icon v-bind="props">
            <v-avatar color="red" size="large" class="pa-6">
              <span class="text-h5">{{ initials }}</span>
            </v-avatar>
          </v-btn>
        </template>
        <v-card color="blue-grey-lighten-2">
          <v-card-text>
            <div class="mx-auto text-center">
              <v-avatar color="red" class="pa-6">
                <span class="text-h5">{{ initials }}</span>
              </v-avatar>
              <h3 class="mt-2">
                {{ fullName }}
              </h3>
              <div class="w-75 mx-auto mt-2">
                <p class="text-caption mt-1 text-start">
                  {{ "Benutzername: " }}
                  <span class="font-weight-bold"
                    >{{ appStore.userData.username }}
                  </span>
                </p>
                <p class="text-caption mt-1 text-start">
                  {{ "Benutzerrechte: " }}
                  <span class="font-weight-bold"
                    >{{ formattedUserGroup }}
                  </span>
                </p>
              </div>
              <v-divider color="white" class="my-3"></v-divider>

              <PasswordReset />
              <!-- <v-btn variant="text" rounded>
                <v-icon class="me-4">mdi-key-variant</v-icon>
                Passwort ändern
              </v-btn> -->
              <v-divider color="white" class="my-3"></v-divider>
              <v-btn @click="signOut" variant="text" rounded>
                <v-icon class="me-4">mdi-logout</v-icon>
                Sign out
              </v-btn>
            </div>
          </v-card-text>
        </v-card>
      </v-menu>
    </v-row>
  </v-container>
</template>

<script setup>
import router from "@/router";
import { useAppStore } from "@/stores/app";
import PasswordReset from "./PasswordReset.vue";
const appStore = useAppStore();
const fullName =
  appStore.userData.first_name + " " + appStore.userData.last_name;

const initials =
  appStore.userData.first_name.charAt(0) +
  appStore.userData.last_name.charAt(0);

const formatUserGroup = (raw) => {
  let capitalized = raw.charAt(0).toUpperCase() + raw.slice(1);
  return capitalized.replace("ue", "ü");
};
const formattedUserGroup = formatUserGroup(appStore.userData.user_group);

const signOut = () => {
  router.push("/login");
};
</script>
