<template>
  <div class="text-center pa-4">
    <v-dialog :model-value="props.showConfirm">
      <v-card
        class="mx-auto my-8 bg-blue-grey-lighten-5 text-blue-grey"
        elevation="16"
      >
        <v-card-title>
          {{ props.hasError ? "Fehler" : "Bestätigung" }}
        </v-card-title>
        <v-card-subtitle class="mb-2">{{
          props.hasError
            ? "Ihre Vorbestellung konnte nicht übermittelt werden"
            : "Ihre Vorbestellung wurde erfolgreich übermittelt"
        }}</v-card-subtitle>
        <div v-if="props.hasError" class="px-4">
          <CustomAlert
            class="mb-3"
            :text="props.errorText"
            icon="$error"
            color="red"
          />
        </div>
        <AnimatedCircle class="mt-2" v-if="!props.hasError" />
        <v-card-actions>
          <v-btn
            class="mb-2 me-2"
            color="blue-grey"
            text="Zurück"
            variant="tonal"
            @click="close"
          ></v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>
<script setup>
import AnimatedCircle from "./AnimatedCircle.vue";
import CustomAlert from "./CustomAlert.vue";

const props = defineProps(["showConfirm", "hasError", "errorText"]);

const emit = defineEmits(["close"]);
const close = () => {
  emit("close");
};
</script>
