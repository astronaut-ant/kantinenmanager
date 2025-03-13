import { defineStore } from "pinia";

export const useFeedbackStore = defineStore("feedbackStore", {
  state: () => ({
    status: "", // 'success', 'error'
    title: "",
    message: "",
    type: "", // 'snackbar', 'dialog'
    show: false,
  }),
  actions: {
    setFeedback(status, type = "snackbar", title = "", message = "Etwas ist schief gelaufen, bitte versuchen Sie es später erneut.") {
      this.status = status;
      this.title = title;
      this.message = message;
      this.type = type;
      this.show = true;
    },
    clearFeedback() {
      this.show = false;
      this.status = "";
      this.title = "";
      this.message = "";
      this.type = "";
    },
  },
});