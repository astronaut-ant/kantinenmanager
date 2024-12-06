<template>
  <NavbarVerwaltung @click="emptyForm" />
  <div class="mt-7 d-flex justify-center" @click="emptyForm">
    <div>
      <v-card class="elevation-7 px-6 py-4 w-100">
        <v-card-text class="mb-2 text-h5"> Neue Gruppe anlegen </v-card-text>
        <CustomAlert
          v-if="noGruppenleiter"
          class="mb-7"
          text="Es existieren keine Gruppenleiter"
          color="red"
          icon="$error"
        />
        <CustomAlert
          v-if="noStandorte"
          class="mb-7"
          text="Es existieren keine Standorte"
          color="red"
          icon="$error"
        />
        <v-form ref="validation" v-model="form" @submit.prevent="handleSubmit">
          <v-text-field
            v-if="!noGruppenleiter && !noStandorte"
            v-model="gruppenName"
            :rules="[required]"
            class="mb-2"
            label="Gruppe"
            required
            clearable
          ></v-text-field>
          <v-select
            class="mb-2"
            v-if="!noGruppenleiter && !noStandorte"
            label="Gruppenleiter"
            v-model="gruppenleitung"
            :rules="[required]"
            :items="gruppenleiterList"
          ></v-select>
          <v-select
            v-if="!noGruppenleiter && !noStandorte"
            label="Standort"
            v-model="standort"
            :rules="[required]"
            :items="standortList"
          ></v-select>

          <v-btn
            v-if="!noGruppenleiter && !noStandorte"
            class="mt-3"
            :disabled="!form"
            color="primary"
            size="large"
            type="submit"
            variant="elevated"
            block
          >
            anlegen
          </v-btn>
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
</template>

<script setup>
import CustomAlert from "@/components/CustomAlert.vue";
import axios from "axios";
const validation = ref("");
const showConfirm = ref(false);
const form = ref(false);
const gruppenName = ref("");
const gruppenleitung = ref(null);
const gruppenleiterList = ref([]);
const noGruppenleiter = ref(false);
const gruppenleiterLookupTable = {};

//Dummy for Location-Endpoint
const standort = ref(null);
const standortList = ref(["W1", "W2", "W3"]);
const noStandorte = ref(false);
const standortLookupTable = {};

//fill Dropdown-Menus and id-Lookup
onMounted(() => {
  axios
    .get("http://localhost:4200/api/users", { withCredentials: true })
    .then((response) => {
      response.data.forEach((user) => {
        if (user.user_group === "gruppenleitung") {
          gruppenleiterLookupTable[`${user.first_name} ${user.last_name}`] =
            user.id;
        }
      });
      if (Object.keys(gruppenleiterLookupTable).length === 0) {
        noGruppenleiter.value = true;
      } else {
        gruppenleiterList.value = Object.keys(gruppenleiterLookupTable);
      }
    })
    .catch((err) => console.log(err));
});

//send to Backend needs Endpoint
const handleSubmit = () => {
  console.log({
    location_name: gruppenName.value,
    user_id: gruppenleiterLookupTable[gruppenleitung.value],
    location_id: standortLookupTable[standort.value],
  });
  axios
    .post("http://localhost:4200/api/groups", {
      location_name: gruppenName.value,
      user_id: gruppenleiterLookupTable[gruppenleitung.value],
      location_id: standortLookupTable[standort.value],
    })
    .then((response) => console.log(response.data))
    .catch((err) => console.log(err));
  showConfirm.value = true;
};

//validate
const required = (v) => {
  return !!v || "Eingabe erforderlich";
};

//emptyForm for new submit
const emptyForm = () => {
  if (showConfirm.value) {
    showConfirm.value = false;
    validation.value.reset();
  }
};
</script>
