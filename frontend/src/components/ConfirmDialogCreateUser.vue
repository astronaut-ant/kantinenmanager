<template>
  <div class="text-center pa-4">
    <v-dialog :model-value="props.showConfirm">
      <v-card
        class="mx-auto my-8"
        elevation="16"
        min-height="400"
        min-width="400"
      >
        <v-card-item class="mb-5">
          <v-card-title> Bestätigung </v-card-title>

          <v-card-subtitle>
            Das Benutzerkonto wurde erfolgreich angelegt
          </v-card-subtitle>
        </v-card-item>
        <v-card-text>
          <div class="mb-12">
            <h2>Benutzername: {{ props.userName }}</h2>
            <h2>Passwort: {{ props.initialPassword }}</h2>
          </div>
          <AnimatedCircle />
        </v-card-text>
        <v-card-actions>
          <v-btn
            class="mb-2 me-4"
            color="primary"
            text="OK"
            variant="elevated"
            @click="close"
          ></v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>

  >
</template>
<script setup>
import AnimatedCircle from "./AnimatedCircle.vue";

const props = defineProps(["showConfirm", "initialPassword", "userName"]);
const emit = defineEmits(["close"]);
const close = () => {
  emit("close");
};
</script>
