<template>
  <v-card width="500" :max-width="500" class="elevation-7 px-6 py-4 mx-auto">
    <v-card-title class="mb-3 text-h5 text-center">
      Standort bearbeiten
    </v-card-title>
    <v-form ref="validation" v-model="form" @submit.prevent="handleSubmit">
      <v-text-field
        v-model="standortName"
        :rules="[required]"
        label="Standort"
        required
        clearable
      ></v-text-field>
      <v-select
        label="Standortleiter"
        class="mb-3 mt-3"
        v-model="standortLeitungSelection"
        :rules="[required]"
        :items="availableStandortleiterItems"
        item-title="name"
        item-value="id"
      ></v-select>
      <v-select
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
      <v-card-actions class="mt-3 justify-end pa-0">
        <v-btn text @click="close">Abbrechen</v-btn>
        <v-btn color="primary" type="submit" variant="elevated"
          >Speichern
        </v-btn>
      </v-card-actions>
    </v-form>
  </v-card>
</template>

<script setup>
import SuccessSnackbar from "@/components/SuccessSnackbar.vue";
import router from "@/router";
import axios from "axios";
const props = defineProps(["oldValues"]);
const emit = defineEmits(["close", "save", "success"]);
const close = () => {
  emit("close");
};
const save = () => {
  emit("save");
};
const success = () => {
  emit("success");
};
const validation = ref("");
const showConfirm = ref(false);
const form = ref(false);
const standortName = ref("");
const standortLeitungSelection = ref();

const kuechenpersonalSelection = ref([]);

const busyStandortleiter = [];
const allStandortLeiter = [];
let availableStandortleiter;
const availableStandortleiterItems = ref([]);
const availableKuechenpersonal = [];
const noKuechenpersonal = ref(false);
const availableKuechenpersonalItems = ref([]);

const oldLocationName = props.oldValues.location_name;
const oldStandorleitungSelection = props.oldValues.location_leader.id;

const oldLocationLeaderObject = {
  first_name: props.oldValues.location_leader.first_name,
  last_name: props.oldValues.location_leader.last_name,
  location_id: props.oldValues.id,
  user_group: props.oldValues.location_leader.user_group,
  username: props.oldValues.location_leader.username,
  id: props.oldValues.location_leader.id,
};
console.log("OLD", props.oldValues);
//get busylist of all locationleader ids;
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
  standortName.value = oldLocationName;
  standortLeitungSelection.value = oldStandorleitungSelection;
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
              (user.location_id === null ||
                user.location_id === props.oldValues.id)
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
            if (kuechenpersonalObject.location_id === props.oldValues.id) {
              kuechenpersonalSelection.value.push(kuechenpersonalObject.id);
            }
          });

          availableStandortleiter = allStandortLeiter.filter(
            (standortleiterObject) => {
              return !busyStandortleiter.includes(standortleiterObject.id);
            }
          );
          availableStandortleiter.push(oldLocationLeaderObject);
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
  console.log(standortLeitungSelection.value);
  availableKuechenpersonal.forEach((kuechenpersonalObject) => {
    if (kuechenpersonalObject.location_id != null) {
      axios.put(
        import.meta.env.VITE_API + `/api/users/${kuechenpersonalObject.id}`,
        {
          first_name: kuechenpersonalObject.first_name,
          last_name: kuechenpersonalObject.last_name,
          user_group: kuechenpersonalObject.user_group,
          username: kuechenpersonalObject.username,
        },
        { withCredentials: true }
      );
    }
    console.log("EP", standortLeitungSelection.value);
    axios
      .put(
        import.meta.env.VITE_API +
          `/api/locations/${oldLocationLeaderObject.location_id}`,
        {
          location_name: standortName.value,
          user_id_location_leader: standortLeitungSelection.value,
        },
        { withCredentials: true }
      )
      .then(() => {
        const kuechenpersonalArrayForRequests = availableKuechenpersonal.filter(
          (kuechenpersonalObject) => {
            return kuechenpersonalSelection.value.includes(
              kuechenpersonalObject.id
            );
          }
        );
        kuechenpersonalArrayForRequests.forEach(
          (kuechenpersonalObject) =>
            (kuechenpersonalObject.location_id =
              oldLocationLeaderObject.location_id)
        );
        kuechenpersonalArrayForRequests.forEach((kuechenpersonalObject) => {
          axios
            .put(
              import.meta.env.VITE_API +
                `/api/users/${kuechenpersonalObject.id}`,
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
        save();
        success();
        close();
      })

      .catch((err) => console.log(err));
  });
};

//validate
const required = (v) => {
  return !!v || "Eingabe erforderlich";
};

//emptyForm for new submit
</script>
