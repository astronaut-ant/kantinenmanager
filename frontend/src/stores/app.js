// Utilities
import { defineStore } from "pinia";

export const useAppStore = defineStore("appStore", {
  state: () => ({ userData: {} }),
});
