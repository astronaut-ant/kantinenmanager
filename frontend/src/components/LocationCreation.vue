<template>
  <div class="mt-7 d-flex justify-center">
    <div>
      <v-card width="500" :max-width="500" class="elevation-7 px-6 py-4">
        <v-card-text class="mb-3 text-h5 text-center">
          Neuen Standort anlegen
        </v-card-text>
        <CustomAlert
          v-if="noStandortleiter"
          class="mb-7"
          text="Es existieren keine vefügbaren Standortleiter "
          color="blue-grey"
          icon="mdi-information-outline"
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
            v-model="standortLeitungSelection"
            :rules="[required]"
            :items="availableStandortleiterItems"
            item-title="name"
            item-value="id"
          ></v-select>
          <v-select
            v-if="!noStandortleiter"
            menu-icon="mdi-chevron-right"
            :menu-props="{ submenu: true, offset: 60 }"
            variant="outlined"
            chips
            color="primary"
            multiple
            label="Küchenpersonal"
            v-model="kuechenpersonalSelection"
            :items="availableKuechenpersonalItems"
            item-title="name"
            item-value="id"
            :disabled="noKuechenpersonal"
          >
          </v-select>

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
      </v-card>
    </div>
  </div>
</template>

<script setup>
import CustomAlert from "@/components/CustomAlert.vue";
import SuccessSnackbar from "@/components/SuccessSnackbar.vue";
import router from "@/router";
import axios from "axios";
const emit = defineEmits(["close"]);
const close = () => {
  emit("close");
};
const validation = ref("");
const showConfirm = ref(false);
const form = ref(false);
const standortName = ref("");
const standortLeitungSelection = ref();
const noStandortleiter = ref(false);

const kuechenpersonalSelection = ref([]);

const busyStandortleiter = [];
const allStandortLeiter = [];
let availableStandortleiter;
const availableStandortleiterItems = ref([]);
const availableKuechenpersonal = [];
const noKuechenpersonal = ref(false);
const availableKuechenpersonalItems = ref([]);

//get busylist of all locationleader ids; check
//get all standortleiter
//find all Standortleiter where locationleader id not in busylist
//get list of available names
//feed v-select standortleiter
//get all available kuechenpersonal with (location_id not null)
//get list of available kpname
//feed v-select kp
//on submit:
// allStandortleiter.find(....)[0]
// post (response.data.id -->)
// allAvailableKuechenpersonal.find(...)
// foreach
//set location.id (from response.data.id)
//post
//emptyForm();
//showConfirm.value = true;
onMounted(() => {
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
    .catch((err) => console.log(err))
    .then(() => {
      axios
        .get(import.meta.env.VITE_API + "/api/users", { withCredentials: true })
        .then((response) => {
          response.data.forEach((user) => {
            if (
              user.user_group === "kuechenpersonal" &&
              user.location_id === null
            ) {
              availableKuechenpersonal.push(user);
            }
            if (user.user_group === "standortleitung") {
              allStandortLeiter.push(user);
            }
          });
          if (availableKuechenpersonal.length === 0) {
            noKuechenpersonal.value = true;
          }
          availableKuechenpersonal.forEach((kuechenpersonalObject) => {
            const name =
              kuechenpersonalObject.first_name +
              " " +
              kuechenpersonalObject.last_name;
            const id = kuechenpersonalObject.id;
            availableKuechenpersonalItems.value.push({ name: name, id: id });
          });

          availableStandortleiter = allStandortLeiter.filter(
            (standortleiterObject) => {
              return !busyStandortleiter.includes(standortleiterObject.id);
            }
          );
          if (availableStandortleiter.length === 0) {
            noStandortleiter.value = true;
          }
          console.log(availableStandortleiter);
          availableStandortleiter.forEach((standortleiterObject) => {
            const name =
              standortleiterObject.first_name +
              " " +
              standortleiterObject.last_name;
            const id = standortleiterObject.id;
            availableStandortleiterItems.value.push({ name: name, id: id });
            console.log("as", availableStandortleiterItems.value);
          });
        });
    })
    .catch((err) => console.log(err));
});

const handleSubmit = () => {
  console.log(standortName.value);
  console.log("EP", standortLeitungSelection.value);
  axios
    .post(
      import.meta.env.VITE_API + "/api/locations",
      {
        location_name: standortName.value,
        user_id_location_leader: standortLeitungSelection.value,
      },
      { withCredentials: true }
    )
    .then((response) => {
      const generatedLocationId = response.data.location_id;
      const kuechenpersonalArrayForRequests = availableKuechenpersonal.filter(
        (kuechenpersonalObject) => {
          return kuechenpersonalSelection.value.includes(
            kuechenpersonalObject.id
          );
        }
      );
      kuechenpersonalArrayForRequests.forEach(
        (kuechenpersonalObject) =>
          (kuechenpersonalObject.location_id = generatedLocationId)
      );
      kuechenpersonalArrayForRequests.forEach((kuechenpersonalObject) => {
        axios
          .put(
            import.meta.env.VITE_API + `/api/users/${kuechenpersonalObject.id}`,
            {
              first_name: kuechenpersonalObject.first_name,
              last_name: kuechenpersonalObject.last_name,
              location_id: kuechenpersonalObject.location_id,
              user_group: kuechenpersonalObject.user_group,
              username: kuechenpersonalObject.username,
            },
            { withCredentials: true }
          )
          .then((response) => console.log(response.data))
          .catch((err) => console.log(err));
      });
    })
    .then(() => {
      close();
    });
};

//validate
const required = (v) => {
  return !!v || "Eingabe erforderlich";
};

//emptyForm for new submit
</script>
