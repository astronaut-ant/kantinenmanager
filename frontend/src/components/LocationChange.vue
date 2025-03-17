<template>
  <v-card :min-width="300" class="elevation-7 px-6 py-4 mx-auto text-blue-grey">
    <v-card-text class="mb-2 text-h6">
      <div class="d-flex ga-4 mt-n3 mb-2 ms-n7 text-primary">
        <div class="d-none d-md-flex align-center mt-n2">
          <v-icon :size="40">mdi-home-edit-outline</v-icon>
        </div>
        <h2>Standort bearbeiten</h2>
      </div>
    </v-card-text>
    <v-form ref="validation" v-model="form" @submit.prevent="handleSubmit">
      <v-text-field
        @update:model-value="hasChanged = true"
        class="mb-5"
        :active="true"
        base-color="blue-grey"
        color="primary"
        variant="outlined"
        Placeholder="Namen des Standorts eingeben"
        v-model="standortName"
        :rules="[required, unique]"
        label="Standort"
        required
        clearable
      ></v-text-field>
      <v-select
        @update:model-value="hasChanged = true"
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
      ></v-select>
      <v-select
        @update:model-value="hasChanged = true"
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
        <template v-slot:chip>
          <v-chip color="primary"> </v-chip>
        </template>
      </v-select>
      <v-card-actions class="mt-3 justify-end pa-0">
        <v-btn text @click="close">{{
          hasChanged ? "Abbrechen" : "Zurück"
        }}</v-btn>
        <v-btn
          :disabled="!hasChanged"
          color="primary"
          type="submit"
          variant="elevated"
          >Übernehmen
        </v-btn>
      </v-card-actions>
    </v-form>
  </v-card>
</template>

<script setup>
import { useFeedbackStore } from "@/stores/feedback";
const feedbackStore = useFeedbackStore();
import router from "@/router";
import axios from "axios";
const props = defineProps(["oldValues"]);
const emit = defineEmits(["close", "save"]);
const close = () => {
  emit("close");
};
const save = () => {
  emit("save");
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
const hasChanged = ref(false);
const allLocationNames = ref([]);

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
        allLocationNames.value.push(location.location_name);
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

/*
const handleSubmit = () => {
  if (noKuechenpersonal.value) {
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
        save();
        success();
        close();
      });
  }
  console.log(standortName.value);
  console.log(standortLeitungSelection.value);
  availableKuechenpersonal.forEach((kuechenpersonalObject) => {
    if (kuechenpersonalObject.location_id != null) {
      axios
        .put(
          import.meta.env.VITE_API + `/api/users/${kuechenpersonalObject.id}`,
          {
            first_name: kuechenpersonalObject.first_name,
            last_name: kuechenpersonalObject.last_name,
            user_group: kuechenpersonalObject.user_group,
            username: kuechenpersonalObject.username,
          },
          { withCredentials: true }
        )
        .then((response) => console.log(response.data));
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
        {
          const kuechenpersonalArrayForRequests =
            availableKuechenpersonal.filter((kuechenpersonalObject) => {
              return kuechenpersonalSelection.value.includes(
                kuechenpersonalObject.id
              );
            });
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
        }
      })
      .catch((err) => {
        console.log(err);
      })
      .then(() => {
        save();
        success();
        close();
      })

      .catch((err) => {
        console.log(err);
        error();
      });
  });
};
*/

const handleSubmit = () => {
  let hasError = false;

  if (noKuechenpersonal.value) {
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
        if (!hasError) {
          save();
          feedbackStore.setFeedback(
            "success",
            "snackbar",
            "",
            "Der Standort wurde erfolgreich aktualisiert"
          );
        }
        close();
      })
      .catch((err) => {
        hasError = true;
        console.error(err);
        feedbackStore.setFeedback(
          "error",
          "snackbar",
          err.response?.data?.title,
          err.response?.data?.description
        );
      });
    return;
  }

  console.log(standortName.value);
  console.log(standortLeitungSelection.value);

  availableKuechenpersonal.forEach((kuechenpersonalObject) => {
    if (kuechenpersonalObject.location_id != null) {
      axios
        .put(
          import.meta.env.VITE_API + `/api/users/${kuechenpersonalObject.id}`,
          {
            first_name: kuechenpersonalObject.first_name,
            last_name: kuechenpersonalObject.last_name,
            user_group: kuechenpersonalObject.user_group,
            username: kuechenpersonalObject.username,
          },
          { withCredentials: true }
        )
        .then((response) => console.log(response.data))
        .catch((err) => {
          hasError = true;
          console.error(err);
          feedbackStore.setFeedback(
            "error",
            "snackbar",
            err.response?.data?.title,
            err.response?.data?.description
          );
        });
    }

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
        if (!hasError) {
          const kuechenpersonalArrayForRequests =
            availableKuechenpersonal.filter((kObj) => {
              return kuechenpersonalSelection.value.includes(kObj.id);
            });
          kuechenpersonalArrayForRequests.forEach(
            (kObj) => (kObj.location_id = oldLocationLeaderObject.location_id)
          );
          kuechenpersonalArrayForRequests.forEach((kObj) => {
            axios
              .put(
                import.meta.env.VITE_API + `/api/users/${kObj.id}`,
                {
                  first_name: kObj.first_name,
                  last_name: kObj.last_name,
                  location_id: kObj.location_id,
                  user_group: kObj.user_group,
                  username: kObj.username,
                },
                { withCredentials: true }
              )
              .then((response) => console.log(response.data))
              .catch((err) => {
                hasError = true;
                console.log(err);
              });
          });
        }
      })
      .catch((err) => {
        hasError = true;
        console.error(err);
        feedbackStore.setFeedback(
          "error",
          "snackbar",
          err.response?.data?.title,
          err.response?.data?.description
        );
      })
      .then(() => {
        if (!hasError) {
          save();
          feedbackStore.setFeedback(
            "success",
            "snackbar",
            "",
            "Der Standort wurde erfolgreich aktualisiert"
          );
        }
        close();
      })
      .catch((err) => {
        hasError = true;
        console.error(err);
        feedbackStore.setFeedback(
          "error",
          "snackbar",
          err.response?.data?.title,
          err.response?.data?.description
        );
      });
  });
};

//validate
const required = (v) => {
  return !!v || "Eingabe erforderlich";
};
const unique = (v) => {
  return (
    !allLocationNames.value.includes(v) ||
    v === oldLocationName ||
    "Standortname bereits vergeben"
  );
};

//emptyForm for new submit
</script>
