<template>
  <v-dialog color="" v-model="dialog" max-width="800">
    <template v-slot:activator="{ props: activatorProps }">
      <v-btn
        v-bind="activatorProps"
        icon="mdi-qrcode"
        class="bg-green"
        size="30"
      ></v-btn>
    </template>

    <v-card class="mx-auto px-4">
      <v-card-text>
        <h2 class="ms-n1 mt-2 mb-6 text-blue-grey font-weight-bold">
          {{ props.firstName }} {{ props.lastName }}
        </h2>
        <qrcode-canvas
          :value="props.qrValue"
          :size="250"
          level="H"
          foreground="#4CAF50"
          background="#ECEFF1"
        />
      </v-card-text>
      <v-card-actions class="pe-5">
        <v-btn
          class="mb-3 mt-n2"
          color="blue-grey"
          text="Zurück"
          variant="tonal"
          @click="close"
        ></v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import QrcodeCanvas from "qrcode.vue";
const dialog = ref(false);
const props = defineProps(["qrValue", "firstName", "lastName"]);

const close = () => {
  dialog.value = false;
};
</script>

<!-- Dummy -->
