<template>
  <NavbarKueche />
  <div class="d-flex h-100 justify-center align-center mt-n10 bg-black">
    <div class="w-50 auto">
      <qrcode-stream
        class="pa-1"
        :paused="!inScanMode"
        @detect="onDetect"
        :track="trackQR"
      >
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
  </div>
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
