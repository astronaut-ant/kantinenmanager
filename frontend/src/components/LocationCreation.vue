<template>
  <div class="mt-14 d-flex justify-center">
    <div>
      <v-card
        :min-width="600"
        class="elevation-7 px-6 py-4 text-blue-grey-darken-3"
      >
        <v-card-text class="mb-2 text-h6">
          <div class="d-flex ga-4 mt-n3 mb-2 ms-2 ms-n4 text-primary">
            <div class="d-flex align-center mt-n2">
              <v-icon :size="40">mdi-home-plus</v-icon>
            </div>
            <h2>Neuen Standort anlegen</h2>
          </div>
        </v-card-text>
        <v-form ref="validation" v-model="form" @submit.prevent="handleSubmit">
          <v-text-field
            class="mb-5 mt-4"
            :active="true"
            base-color="blue-grey"
            color="primary"
            variant="outlined"
            Placeholder="Namen des Standorts eingeben"
            v-model="standortName"
            :rules="[required]"
            label="Standort"
            required
            clearable
          ></v-text-field>
          <v-select
            :active="true"
            base-color="blue-grey"
            color="primary"
            variant="outlined"
            Placeholder="Verfügbaren Standortleiter auswählen"
            label="Standortleiter"
            class="mb-5 mt-3"
            v-model="standortLeitungSelection"
            :rules="[required]"
            :items="availableStandortleiterItems"
            item-title="name"
            item-value="id"
            no-data-text="Keine freien Standortleiter mehr verfügbar"
          ></v-select>
          <v-select
            class="mb-6 mt-3"
            :active="true"
            base-color="blue-grey"
            color="primary"
            variant="outlined"
            Placeholder="Verfügbares Küchenpersonal zuweisen"
            chips
            multiple
            label="Küchenpersonal"
            v-model="kuechenpersonalSelection"
            :items="availableKuechenpersonalItems"
            item-title="name"
            item-value="id"
            no-data-text="Kein freies Küchenpersonal mehr verfügbar"
          >
            <!-- "noKuechenpersonal" -->
            <template v-slot:chip>
              <v-chip color="primary"> </v-chip>
            </template>
          </v-select>

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
        <slot name="confirm"></slot>
      </v-card>
    </div>
  </div>
</template>

<script setup>
import CustomAlert from "@/components/CustomAlert.vue";
import router from "@/router";
import axios from "axios";
import { useFeedbackStore } from "@/stores/feedback";
const feedbackStore = useFeedbackStore();
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
    .catch((err) => {
      console.error(err);
      feedbackStore.setFeedback("error", "snackbar", err.response?.data?.title, err.response?.data?.description);
    })
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
    .catch((err) => {
      console.error(err);
      feedbackStore.setFeedback("error", "snackbar", err.response?.data?.title, err.response?.data?.description);
    });
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
          .catch((err) => {
            console.error(err);
            feedbackStore.setFeedback("error", "snackbar", err.response?.data?.title, err.response?.data?.description);
          });
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

const emptyForm = () => {
  showConfirm.value = false;
  validation.value.reset();
};
</script>
