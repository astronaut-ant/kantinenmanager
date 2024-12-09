<template>
  <v-dialog
    :model-value="props.showDialog"
    max-width="500"
    :persistent="true"
    :no-click-animation="true"
  >
    <v-form v-model="form">
      <v-card :title="'Bestellformular anlegen für ' + props.date">
        <v-card-text
          ><v-select
            v-if="!dropdownDisabled"
            required
            :rules="[required]"
            label="Wähle Gruppe"
            v-model="selectedGroup"
            :items="props.groups"
          ></v-select>
          <div v-if="dropdownDisabled" class="d-flex justify-center">
            <v-chip color="#607D8B" size="large">{{ selectedGroup }}</v-chip>
          </div>
        </v-card-text>

        <v-card-actions>
          <v-spacer></v-spacer>

          <v-btn text="Abbrechen" @click="close"></v-btn>
          <v-btn
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
const dropdownDisabled = ref(false);
const emit = defineEmits(["close", "save"]);
const close = () => {
  emit("close");
};
const save = () => {
  emit("save", selectedGroup.value);
  emit("close");
};
onMounted(() => {
  if (props.groups.length < 2) {
    selectedGroup.value = props.groups[0];
    dropdownDisabled.value = true;
  } else {
    dropdownDisabled.value = false;
  }
});
const required = (v) => {
  return !!v || "Eingabe erforderlich";
};
</script>
