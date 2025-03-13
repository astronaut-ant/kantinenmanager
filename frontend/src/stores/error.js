import { defineStore } from "pinia";

export const useErrorStore = defineStore("errorStore", {
  state: () => ({
    message: "",
    type: "", // 'snackbar', 'banner', 'dialog'
    show: false,
  }),
  actions: {
    setError(message, type = "snackbar") {
      this.message = message;
      this.type = type;
      this.show = true;
    },
    clearError() {
      this.show = false;
      this.message = "";
      this.type = "";
    },
  },
});