<template>
  <div class="text-center pa-4">
    <v-dialog :model-value="props.showConfirm">
      <v-card
        class="mx-auto my-8 bg-blue-grey-lighten-5 text-blue-grey"
        elevation="16"
      >
        <v-card-title> Bestätigung </v-card-title>
        <v-card-subtitle class="mb-4"
          >Ihre Vorbestellung wurde erfolgreich übermittelt</v-card-subtitle
        >
        <AnimatedCircle />
        <v-card-actions>
          <v-btn
            class="mb-2 me-4"
            color="primary"
            text="Zurück"
            variant="elevated"
            @click="close"
          ></v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>
<script setup>
import AnimatedCircle from "./AnimatedCircle.vue";

const props = defineProps([
  "showConfirm",
  "initialPassword",
  "userName",
  "userGroup",
  "text",
]);

const groupCreated = ref(false);
const locationCreated = ref(false);
console.log(props.userGroup);
groupCreated.value = props.userGroup == "gruppenleitung";
locationCreated.value = props.userGroup == "standortleitung";

const emit = defineEmits(["close"]);
const close = () => {
  emit("close");
};
</script>
