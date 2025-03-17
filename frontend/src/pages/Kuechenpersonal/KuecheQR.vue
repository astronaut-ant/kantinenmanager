<template>
  <NavbarKueche :breadcrumbs="[{ title: 'QR-Scanner' }]" />
  <v-container
    min-width="100vw"
    min-height="100vh"
    class="bg-black d-flex align-center"
  >
    <div class="w-50 auto mx-auto">
      <qrcode-stream :paused="!inScanMode" @detect="onDetect" :track="trackQR">
        <div
          class="position-absolute w-100 h-100 border-primary rounded elevation-2"
        >
          <ScannedOrder
            v-if="!inScanMode"
            @close="inScanMode = !inScanMode"
            :data="qrMessage"
          />
        </div>
      </qrcode-stream>
    </div>
  </v-container>
</template>

<script setup>
const inScanMode = ref(true);

import { QrcodeStream, QrcodeDropZone, QrcodeCapture } from "vue-qrcode-reader";
const qrMessage = ref({});

const onDetect = (detectedCode) => {
  qrMessage.value = detectedCode;
  inScanMode.value = !inScanMode.value;
};

const trackQR = (detectedCodes, ctx) => {
  for (const detectedCode of detectedCodes) {
    const {
      boundingBox: { x, y, width, height },
    } = detectedCode;

    ctx.lineWidth = 2;
    ctx.strokeStyle = "#F44336";
    ctx.strokeRect(x, y, width, height);
  }
};
</script>
