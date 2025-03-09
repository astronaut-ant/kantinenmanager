<template>
    <div class="grid-container">
      <div class="grid-item" v-for="(item, index) in items" :key="index">
        <slot :item="item"></slot>
      </div>
    </div>
</template>
  
<script setup>
  import { defineProps } from "vue";
  
  defineProps({
    items: {
      type: Array,
      default: () => [],
    },
  });
</script>
  
<style scoped>
  .grid-container {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(425px, 1fr));
    gap: 10px;
    justify-content: center;
    justify-items: center;
    padding: 20px;
    width: 100%;
    max-width: 100%;
    box-sizing: border-box;
  }
  
  .grid-item {
    display: flex;
    justify-content: center;
    align-items: flex-start;
    min-width: 400px;
    max-width: 425px;
  }
</style>
