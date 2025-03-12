<template>
  <NavbarVerwaltung
    :breadcrumbs="[{ title: 'Gruppen' }, { title: 'Neue Gruppe' }]"
  />
  <div class="mt-14 d-flex justify-center">
    <div>
      <v-card :min-width="600" class="elevation-7 px-6 py-4 w-100">
        <v-card-text class="mb-2 text-h6">
          <div class="d-flex ga-4 mt-n3 mb-2 ms-2 ms-n3 text-primary">
            <div class="d-flex align-center mt-n2 ms-n1">
              <v-icon :size="40">mdi-account-group</v-icon>
              <v-icon class="ms-n1" :size="30">mdi-plus</v-icon>
            </div>
            <h2>Neue Gruppe anlegen</h2>
          </div>
        </v-card-text>
        <!-- <CustomAlert
          v-if="noGruppenleiter"
          class="mb-7"
          text="Es existieren keine Gruppenleiter"
          color="blue-grey"
          icon="mdi-information-outline"
        />
        <CustomAlert
          v-if="noStandorte"
          class="mb-7"
          text="Es existieren keine Standorte"
          color="blue-grey"
          icon="mdi-information-outline"
        /> -->

        <v-form ref="validation" v-model="form" @submit.prevent="handleSubmit">
          <div class="d-flex ga-8 mb-2 mt-4">
            <v-text-field
              :active="true"
              base-color="blue-grey"
              color="primary"
              variant="outlined"
              v-model="gruppenName"
              :rules="[required]"
              class="mb-2 w-100"
              label="Gruppenname"
              placeholder="Namen der Gruppe eingeben"
              required
              clearable
            ></v-text-field>
            <v-container class="pa-0">
              <v-number-input
                hide-details="auto"
                precision="0"
                :active="true"
                base-color="blue-grey"
                color="primary"
                control-variant="default"
                inset
                variant="outlined"
                v-model="gruppenNr"
                :rules="[required, unique]"
                class="w-100"
                label="Gruppennummer"
                placeholder="Nummer zuweisen"
                :min="1"
                required
                clearable
              ></v-number-input>
            </v-container>
          </div>
          <!-- <v-text-field
            v-if="!noGruppenleiter && !noStandorte"
            :active="true"
            base-color="blue-grey"
            color="primary"
            variant="outlined"
            v-model="gruppenNr"
            :rules="[required]"
            class="mb-2"
            label="Gruppennummer"
            required
            clearable
            type="number"
          ></v-text-field> -->

          <v-select
            :active="true"
            base-color="blue-grey"
            color="primary"
            variant="outlined"
            class="mb-5 mt-2"
            label="Gruppenleiter"
            Placeholder="Verfügbaren Gruppenleiter auswählen"
            v-model="gruppenleitung"
            :rules="[required]"
            :items="gruppenleiterList"
          ></v-select>
          <v-select
            :active="true"
            base-color="blue-grey"
            color="primary"
            variant="outlined"
            class="mb-4"
            label="Standort"
            Placeholder="Standort auswählen"
            v-model="standort"
            :rules="[required]"
            :items="allLocations"
          ></v-select>
          <v-card-actions class="justify-end me-n2">
            <v-btn @click="emptyForm" color="blue-grey" variant="text">
              Verwerfen
            </v-btn>
            <v-btn
              :disabled="!form"
              color="primary"
              type="submit"
              variant="elevated"
            >
              anlegen
            </v-btn>
          </v-card-actions>
        </v-form>
        <div
          v-if="showConfirm"
          class="mt-5 d-flex justify-center align-center ga-5"
        >
          <h3>Hinzugefügt!</h3>
          <v-icon color="success" icon="mdi-check-circle-outline" size="32">
          </v-icon>
        </div>
      </v-card>
    </div>
  </div>
  <ErrorSnackbar
    v-model="errorSnackbar"
    :text="errorSnackbarText"
    @close="errorSnackbar = false"
  ></ErrorSnackbar>
</template>

<script setup>
import CustomAlert from "@/components/CustomAlert.vue";
import axios from "axios";
const validation = ref("");
const showConfirm = ref(false);
const form = ref(false);
const gruppenNr = ref(null);
const gruppenName = ref("");
const gruppenleitung = ref(null);
const gruppenleiterList = ref([]);
const noGruppenleiter = ref(false);
const gruppenleiterLookupTable = {};
const errorSnackbar = ref(false);
const errorSnackbarText = ref("");

//Dummy for Location-Endpoint
const standort = ref();
const allLocations = ref([]);
const noStandorte = ref(false);
const standortLookupTable = {};
const blockedGroupnumbers = [];

//fill Dropdown-Menus and id-Lookup
const getData = () => {
  // Gruppenleiter laden
  axios
    .get(import.meta.env.VITE_API + "/api/users/group-leaders", {
      withCredentials: true,
    })
    .then((response) => {
      response.data.forEach((user) => {
        if (user.own_group === null)
          gruppenleiterLookupTable[`${user.first_name} ${user.last_name}`] =
            user.id;
      });
      if (Object.keys(gruppenleiterLookupTable).length === 0) {
        noGruppenleiter.value = true;
      } else {
        gruppenleiterList.value = Object.keys(gruppenleiterLookupTable);
      }
    })
    .catch((err) => console.log(err));

  axios
    .get(import.meta.env.VITE_API + "/api/groups", {
      withCredentials: true,
    })
    .then((response) => {
      response.data.forEach((group) => {
        blockedGroupnumbers.push(group.group_number);
        console.log("Blocked: ", blockedGroupnumbers);
      });
    })
    .catch((err) => console.log(err));

  axios
    .get(import.meta.env.VITE_API + "/api/locations", { withCredentials: true })
    .then((response) => {
      response.data.forEach((location) => {
        allLocations.value.push(location.location_name);
      });
      response.data.forEach((location) => {
        standortLookupTable[location.location_name] = location.id;
        console.log(location);
      });
      console.log(standortLookupTable);
      if (Object.keys(standortLookupTable).length === 0) {
        noStandorte.value = true;
      }
      console.log(allLocations.value);
    })
    .catch((err) => console.log(err.response.data.description));
};

//send to Backend needs Endpoint
const handleSubmit = () => {
  axios
    .post(
      import.meta.env.VITE_API + "/api/groups",
      {
        group_number: gruppenNr.value,
        group_name: gruppenName.value,
        location_id: standortLookupTable[standort.value],
        user_id_group_leader: gruppenleiterLookupTable[gruppenleitung.value],
      },
      { withCredentials: true }
    )
    .then((response) => {
      console.log(response.data);
      showConfirm.value = true;
      emptyForm();
    })
    .catch((err) => {
      console.log(err.response.data.description);
      errorSnackbarText.value = "Fehler beim erstellen der Gruppe!";
      errorSnackbar.value = true;
    });
};

//validate
const required = (v) => {
  return !!v || "Eingabe erforderlich";
};
const unique = (v) => {
  return !blockedGroupnumbers.includes(v) || "Gruppe bereits vergeben";
};

//emptyForm for new submit
const emptyForm = () => {
  showConfirm.value = false;
  validation.value.reset();
};
getData();
</script>
<style scoped>
.v-select .v-btn--decrement {
  background-color: #4caf50; /* Green background for decrement button */
  color: white; /* Text color */
  border-radius: 50%; /* Round buttons */
  width: 40px;
  height: 40px;
}
</style>
