<template>
  <v-dialog
    :model-value="props.showDialog"
    max-width="500"
    :persistent="true"
    :no-click-animation="true"
  >
    <v-card :title="'Bestellformular anlegen für ' + props.date">
      <v-card-text
        ><v-select
          label="Wähle Gruppe"
          v-model="selectedGroup"
          :items="groups"
        ></v-select>
      </v-card-text>

      <v-card-actions>
        <v-spacer></v-spacer>

        <v-btn text="Abbrechen" @click="close"></v-btn>
        <v-btn
          class="bg-primary"
          text="Bestellformular anlegen"
          @click="save"
        ></v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { onMounted } from "vue";

const groups = ref(["Gruppe 1", "Gruppe 2 (Vertretung)"]);
const props = defineProps(["showDialog", "date"]);
const selectedGroup = ref("Gruppe 1");
const emit = defineEmits(["close", "save"]);
const close = () => {
  emit("close");
};
const save = () => {
  emit("save", selectedGroup.value);
  emit("close");
};
onMounted(() => {
  selectedGroup.value = "Gruppe 1";
});
</script>
