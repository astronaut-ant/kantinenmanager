<template>
  <NavbarVerwaltung />
  <div class="mt-7 d-flex justify-center">
    <div>
      <v-card width="500" :max-width="500" class="elevation-7 px-6 py-4">
        <v-card-text class="mb-3 text-h5 text-center">
          Neuen Standort anlegen
        </v-card-text>
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
            label="Standort"
            required
            clearable
          ></v-text-field>
          <v-select
            v-if="!noStandortleiter"
            label="Standortleiter"
            class="mb-3 mt-3"
            v-model="standortLeitung"
            :rules="[required]"
            :items="standortleiterList"
          ></v-select>
          <v-select
            v-if="!noStandortleiter"
            menu-icon="mdi-chevron-right"
            :menu-props="{ submenu: true }"
            variant="outlined"
            chips
            color="primary"
            multiple
            label="Kuechenpersonal"
            v-model="kuechenpersonal"
            :items="availableKuechenpersonalList"
          >
            <template v-slot:selection="{ item, index }">
              <v-chip v-if="index < 2">
                <span>{{ item.title }}</span>
              </v-chip>
              <span
                v-if="index === 2"
                class="text-grey text-caption align-self-center"
              >
                (+{{ value.length - 2 }} others)
              </span>
            </template></v-select
          >

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

const kuechenpersonalLookupTable = {};
const kuechenpersonal = ref([]);
const availableKuechenpersonalList = ref([]);

const busyStandortleiter = [];
const allStandortLeiter = [];
let availableStandortleiter;

//get busylist of all locationleader ids; check
//get all standortleiter
//find all Standortleiter where locationleader id not in busylist
//get list of available names
//feed v-select standortleiter
//get all available kuechenpersonal with (location_id not null)
//get list of available kpname
//feed v-select standortleiter
//on submit:
// allStandortleiter.find(....)[0]
// post (response.data.id -->)
// allAvailableKuechenpersonal.find(...)
// foreach
//set location.id (from response.data.id)
//post
//emptyForm();
//showConfirm.value = true;

axios
  .get(import.meta.env.VITE_API + "/api/locations", { withCredentials: true })
  .then((response) => {
    const allLocations = response.data;
    console.log(allLocations);

    allLocations.forEach((location) => {
      busyStandortleiter.push(location.location_leader.id);
      console.log(busyStandortleiter);
    });
  })
  .then(() => {
    axios
      .get(import.meta.env.VITE_API + "/api/users", { withCredentials: true })
      .then((response) => {
        response.data.forEach((user) => {
          if (user.user_group === "standortleitung") {
            allStandortLeiter.push(user);
          }
        });
        console.log(allStandortLeiter);
        availableStandortleiter = allStandortLeiter.filter(
          (standortleiterObjekt) => {
            return !busyStandortleiter.includes(standortleiterObjekt.id);
          }
        );
      });
  });

//   });

//     if (user.user_group === "kuechenpersonal" && user.location_id === null) {
//       kuechenpersonalLookupTable[`${user.first_name} ${user.last_name}`] =
//         user.id;
//     }
//   });
//   if (Object.keys(standortLeiterLookupTable).length === 0) {
//     noStandortleiter.value = true;
//   } else {
//     standortleiterList.value = Object.keys(standortLeiterLookupTable);
//     availableKuechenpersonalList.value = Object.keys(
//       kuechenpersonalLookupTable
//     );
//   }
// })
// .catch((err) => console.log(err));

//send to Backend needs Endpoint
const handleSubmit = () => {
  // console.log({
  //   location_name: standortName.value,
  //   user_id: standortLeiterLookupTable[standortLeitung.value],
  // });
  // axios
  //   .post(
  //     import.meta.env.VITE_API + "/api/locations",
  //     {
  //       location_name: standortName.value,
  //       user_id_location_leader:
  //         standortLeiterLookupTable[standortLeitung.value],
  //     },
  //     { withCredentials: true }
  //   )
  //   .then((response) => {
  //     console.log(response.data);
  //     const newLocationId = response.data.id
  //     kuechenpersonal.value.forEach((name) => {
  //       kuechenpersonalLookupTable
  //       {user.location_id:newLocationId
  //       }
  //       axios.put(
  //         import.meta.env.VITE_API +
  //           `/api/users/${kuechenpersonalLookupTable[name]}`,
  //         {},
  //         { withCredentials: true }
  //       );
  //       emptyForm();
  //       showConfirm.value = true;
  //     });
  //   })
  //   .catch((err) => console.log(err));
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
