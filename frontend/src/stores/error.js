import { defineStore } from "pinia";

export const useErrorStore = defineStore("errorStore", {
  state: () => ({
    title: "",
    message: "",
    type: "", // 'snackbar', 'dialog'
    show: false,
  }),
  actions: {
    setError(title, message, type = "snackbar") {
      this.title = title;
      this.message = message;
      this.type = type;
      this.show = true;
    },
    clearError() {
      this.title = "";
      this.show = false;
      this.message = "";
      this.type = "";
    },
  },
});