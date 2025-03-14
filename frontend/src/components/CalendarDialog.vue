<template>
  <v-dialog
    :model-value="props.showDialog"
    max-width="500"
    :persistent="true"
    :no-click-animation="true"
  >
    <v-form v-model="form" @submit.prevent="init">
      <v-card>
        <v-card-title class="text-blue-grey-darken-3 ms-2 mt-3"
          >Bestellformular anlegen für den
          {{ formatDate(props.date) }}</v-card-title
        >
        <v-card-text
          ><v-select
            v-if="!onlyOne && !noGroupsLeft && !timeLimitExceeded"
            :active="true"
            base-color="blue-grey"
            color="primary"
            variant="outlined"
            class="mt-0"
            placeholder="adkjlsf"
            required
            :rules="[required]"
            label="Gruppe"
            v-model="selectedGroup"
            :items="props.groups"
          ></v-select>
          <div
            v-if="onlyOne && !timeLimitExceeded"
            class="d-flex justify-center"
          >
            <v-chip class="mt-3" color="#4CAF50" size="large">{{
              selectedGroup
            }}</v-chip>
          </div>
          <CustomAlert
            color="red"
            icon="$error"
            text="Für dieses Datum sind bereits alle verfügbaren Bestellformulare angelegt!"
            v-if="noGroupsLeft && !timeLimitExceeded"
          />
          <CustomAlert
            color="red"
            icon="$error"
            text="Frist für Vorbestellungen abgelaufen: Keine weiteren Bestellformulare verfügbar"
            v-if="timeLimitExceeded"
          />
        </v-card-text>

        <v-card-actions class="me-4 mb-3">
          <v-spacer></v-spacer>

          <v-btn
            variant="text"
            color="blue-grey"
            :text="
              noGroupsLeft || timeLimitExceeded ? 'Schließen' : 'Abbrechen'
            "
            @click="close"
          ></v-btn>
          <v-btn
            v-if="!noGroupsLeft && !timeLimitExceeded"
            :disabled="!form"
            class="bg-primary"
            text="Bestellformular anlegen"
            type="submit"
          ></v-btn>
        </v-card-actions>
      </v-card>
    </v-form>
  </v-dialog>
</template>

<script setup>
import { onMounted } from "vue";
import CustomAlert from "./CustomAlert.vue";

// const groups = ref(["Gruppe 1", "Gruppe 2 (Vertretung)"]);
const form = ref(false);
const props = defineProps(["showDialog", "date", "groups", "stopHour"]);
const selectedGroup = ref("");
const onlyOne = ref(false);
const noGroupsLeft = ref(false);
const timeLimitExceeded = ref(false);

const today = new Date();
if (
  props.date === today.toISOString().split("T")[0] &&
  today.getHours() >= props.stopHour
) {
  timeLimitExceeded.value = true;
}

const formatDate = (dateString) => {
  const dateStringArray = dateString.split("-");
  return dateStringArray.reverse().join(".");
};
const emit = defineEmits(["close", "init"]);
const close = () => {
  emit("close");
};
const init = () => {
  emit("init", selectedGroup.value, props.date);
  emit("close");
};
onMounted(() => {
  if (props.groups.length === 1) {
    selectedGroup.value = props.groups[0];
    onlyOne.value = true;
  } else if (props.groups.length === 0) {
    noGroupsLeft.value = true;
  } else {
    onlyOne.value = false;
    noGroupsLeft.value = false;
  }
});
const required = (v) => {
  return !!v || "Eingabe erforderlich";
};
</script>
