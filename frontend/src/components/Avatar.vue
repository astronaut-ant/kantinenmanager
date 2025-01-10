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
        <v-card color="blue-grey-lighten-5">
          <v-card-text>
            <div class="mx-auto text-center">
              <v-avatar color="red" class="pa-6">
                <span class="text-h5">{{ initials }}</span>
              </v-avatar>
              <h3 class="mt-2 text-blue-grey">
                {{ fullName }}
              </h3>
              <div class="w-100 mt-4 mt-2 ps-4">
                <p
                  class="text-caption mt-1 text-start text-no-wrap text-blue-grey"
                >
                  {{ "Benutzername: " }}
                  <span class="font-weight-bold text-blue-grey"
                    >{{ appStore.userData.username }}
                  </span>
                </p>
                <p
                  class="text-caption mt-1 text-start text-no-wrap text-blue-grey"
                >
                  {{ "Benutzerrechte: " }}
                  <span class="font-weight-bold"
                    >{{ formattedUserGroup }}
                  </span>
                </p>
              </div>
              <v-divider color="text-blue-grey" class="my-3"></v-divider>
              <UserFoodOrder />
              <div>
                <UserQRCode />
              </div>
              <v-divider color="text-blue-grey" class="my-3"></v-divider>
              <PasswordChange @succeeded="signOut" />

              <v-divider color="text-blue-grey" class="my-3"></v-divider>
              <div class="text-start">
                <v-btn @click="signOut" variant="text" class="text-blue-grey">
                  <v-icon class="me-4">mdi-logout</v-icon>
                  Abmelden
                </v-btn>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-menu>
    </v-row>
  </v-container>
</template>

<script setup>
import axios from "axios";
import router from "@/router";
import { useAppStore } from "@/stores/app";
import PasswordChange from "./PasswordChange.vue";
import UserFoodOrder from "./UserFoodOrder.vue";
import UserQRCode from "./UserQRCode.vue";
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
  appStore.userData = {};
  axios
    .post(
      import.meta.env.VITE_API + "/api/logout",
      {},
      { withCredentials: true }
    )
    .then(() => {
      router.push("/login");
    })
    .catch((error) => console.log(error));
};
</script>
