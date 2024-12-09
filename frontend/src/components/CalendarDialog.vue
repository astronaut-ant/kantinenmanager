<template>
  <v-dialog
    :model-value="props.showDialog"
    max-width="500"
    :persistent="true"
    :no-click-animation="true"
  >
    <v-form v-model="form">
      <v-card
        :title="'Bestellformular anlegen für den ' + formatDate(props.date)"
      >
        <v-card-text
          ><v-select
            v-if="!onlyOne && !noGroupsLeft"
            class="mt-3"
            required
            :rules="[required]"
            label="Wähle Gruppe"
            v-model="selectedGroup"
            :items="props.groups"
          ></v-select>
          <div v-if="onlyOne" class="d-flex justify-center">
            <v-chip class="mt-3" color="#607D8B" size="large">{{
              selectedGroup
            }}</v-chip>
          </div>
          <CustomAlert
            color="red"
            icon="$error"
            text="Für dieses Datum sind bereits alle verfügbaren Bestellformulare angelegt!"
            v-if="noGroupsLeft"
          />
        </v-card-text>

        <v-card-actions>
          <v-spacer></v-spacer>

          <v-btn
            :text="noGroupsLeft ? 'Schließen' : 'Abbrechen'"
            @click="close"
          ></v-btn>
          <v-btn
            v-if="!noGroupsLeft"
            :disabled="!form"
            class="bg-primary me-3"
            text="Bestellformular anlegen"
            type="submit"
            @click="save"
          ></v-btn>
        </v-card-actions>
      </v-card>
    </v-form>
  </v-dialog>
</template>

<script setup>
import { onMounted } from "vue";

// const groups = ref(["Gruppe 1", "Gruppe 2 (Vertretung)"]);
const form = ref(false);
const props = defineProps(["showDialog", "date", "groups"]);
const selectedGroup = ref("");
const onlyOne = ref(false);
const noGroupsLeft = ref(false);
const formatDate = (dateString) => {
  const dateStringArray = dateString.split("-");
  return dateStringArray.reverse().join(".");
};
const emit = defineEmits(["close", "save"]);
const close = () => {
  emit("close");
};
const save = () => {
  emit("save", selectedGroup.value);
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
