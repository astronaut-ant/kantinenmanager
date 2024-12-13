<template>
  <div class="text-center">
    <v-progress-circular
      :model-value="value"
      :rotate="360"
      :size="80"
      :width="7"
      color="success"
    >
      <template v-slot:default>
        <h1 v-if="showCheck"><v-icon>mdi-check</v-icon></h1>
      </template>
    </v-progress-circular>
  </div>
</template>
<script>
export default {
  data() {
    return {
      showCheck: false,
      interval: -1,
      value: 0,
    };
  },
  mounted() {
    this.interval = setInterval(() => {
      if (this.value === 100) {
        this.showCheck = true;
        return clearInterval(this.interval);
      }
      this.value += 20;
    }, 50);
  },
  beforeUnmount() {
    clearInterval(this.interval);
  },
};
</script>
