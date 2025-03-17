/**
 * plugins/vuetify.js
 *
 * Framework documentation: https://vuetifyjs.com`
 */

// Styles
import "@mdi/font/css/materialdesignicons.css";
import "vuetify/styles";

// Composables
import { createVuetify } from "vuetify";
import { de, en } from "vuetify/locale";

//components
import { VNumberInput } from "vuetify/labs/VNumberInput";

// https://vuetifyjs.com/en/introduction/why-vuetify/#feature-guides
export default createVuetify({
  theme: {
    defaultTheme: "light",
  },
  locale: {
    locale: "de",
    fallback: "en",
    messages: { de, en },
  },
  components: {
    VNumberInput,
  },
});
