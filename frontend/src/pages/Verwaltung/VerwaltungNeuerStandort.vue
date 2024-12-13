<template>
  <NavbarVerwaltung @click="emptyForm" />
  <div class="mt-7 d-flex justify-center" @click="emptyForm">
    <div>
      <v-card class="elevation-7 px-6 py-4 w-100">
        <v-card-text class="mb-2 text-h5"> Neuen Standort anlegen </v-card-text>
        <CustomAlert
          v-if="noStandortleiter"
          class="mb-7"
          text="Es existieren keine Standortleiter "
          color="red"
          icon="$error"
        />
        <v-form ref="validation" v-model="form" @submit.prevent="handleSubmit">
          <v-text-field
            v-if="!noStandortleiter"
            v-model="standortName"
            :rules="[required]"
            class="mb-2"
            label="Standort"
            required
            clearable
          ></v-text-field>
          <v-select
            v-if="!noStandortleiter"
            label="Standortleiter"
            v-model="standortLeitung"
            :rules="[required]"
            :items="standortleiterList"
          ></v-select>

          <v-btn
            v-if="!noStandortleiter"
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
const standortName = ref("");
const standortLeitung = ref(null);
const standortleiterList = ref([]);
const noStandortleiter = ref(false);
const standortLeiterLookupTable = {};

//fill Dropdown-Menu and id-Lookup
onMounted(() => {
  axios
    .get(import.meta.env.VITE_API + "/api/users", { withCredentials: true })
    .then((response) => {
      response.data.forEach((user) => {
        if (user.user_group === "standortleitung") {
          standortLeiterLookupTable[`${user.first_name} ${user.last_name}`] =
            user.id;
        }
      });
      if (Object.keys(standortLeiterLookupTable).length === 0) {
        noStandortleiter.value = true;
      } else {
        standortleiterList.value = Object.keys(standortLeiterLookupTable);
      }
    })
    .catch((err) => console.log(err));
});

//send to Backend needs Endpoint
const handleSubmit = () => {
  console.log({
    location_name: standortName.value,
    user_id: standortLeiterLookupTable[standortLeitung.value],
  });
  axios
    .post(import.meta.env.VITE_API + "/api/locations", {
      location_name: standortName.value,
      user_id: standortLeiterLookupTable[standortLeitung.value],
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
