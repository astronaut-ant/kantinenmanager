<template>
  <v-dialog color="" v-model="dialog" max-width="800">
    <template v-slot:activator="{ props: activatorProps }">
      <div class="text-start">
        <v-btn variant="text" v-bind="activatorProps" class="text-blue-grey"
          ><v-icon class="me-4">mdi-qrcode</v-icon>Mein QR-Code</v-btn
        >
      </div>
    </template>

    <v-card class="mx-auto px-4" color="blue-grey-lighten-5">
      <v-card-text>
        <h2 class="ms-n1 mt-2 mb-6 text-blue-grey font-weight-bold">
          <v-icon class="me-4 text-blue-grey"> mdi-qrcode</v-icon>
          Mein QR-Code
        </h2>
        <qrcode-canvas
          :value="props.qrValue"
          :size="250"
          level="H"
          foreground="#1867C0"
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
const props = defineProps(["qrValue"]);

const close = () => {
  dialog.value = false;
};
</script>

<!-- Dummy -->
