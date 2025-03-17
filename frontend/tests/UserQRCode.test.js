import { describe, it, expect, beforeEach } from "vitest";
import { mount } from "@vue/test-utils";
import { createPinia } from "pinia";
import { createVuetify } from "vuetify";
import { createApp } from "vue";

import "vuetify/styles"; // Make sure to import Vuetify's styles

import UserQRCode from "../src/components/UserQRCode.vue";

describe("UserQRCode", () => {
  let pinia;
  let vuetify;

  beforeEach(() => {
    // Create a new Pinia instance for each test to avoid state pollution
    pinia = createPinia();
    vuetify = createVuetify();

    // Create a Vue app instance and apply Vuetify and Pinia
    const app = createApp(UserQRCode);
    app.use(vuetify); // Apply Vuetify to the app
    app.use(pinia); // Apply Pinia to the app
  });

  it("mounts correctly with props", async () => {
    // Now mount the CalendarDialog component directly
    const wrapper = mount(UserQRCode, {
      global: {
        plugins: [vuetify, pinia], // Pass the vuetify and pinia plugins to the test mount
      },
      props: {
        qrValue: 123,
      },
    });

    expect(wrapper.props().qrValue).toBe(123); // Make sure the component is mounted

    // Make sure the component is mounted
  });
});
