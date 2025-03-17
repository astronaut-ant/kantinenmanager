import { describe, it, expect, beforeEach } from "vitest";
import { mount } from "@vue/test-utils";
import { createPinia } from "pinia";
import { createVuetify } from "vuetify";
import { createApp } from "vue";

import "vuetify/styles"; // Make sure to import Vuetify's styles

import CalendarDialog from "../src/components/CalendarDialog.vue";

describe("CalendarDialog", () => {
  let pinia;
  let vuetify;

  beforeEach(() => {
    // Create a new Pinia instance for each test to avoid state pollution
    pinia = createPinia();
    vuetify = createVuetify();

    // Create a Vue app instance and apply Vuetify and Pinia
    const app = createApp(CalendarDialog);
    app.use(vuetify); // Apply Vuetify to the app
    app.use(pinia); // Apply Pinia to the app
  });

  it("mounts correctly with props", async () => {
    // Now mount the CalendarDialog component directly
    const wrapper = mount(CalendarDialog, {
      global: {
        plugins: [vuetify, pinia], // Pass the vuetify and pinia plugins to the test mount
      },
      props: {
        stopHour: 8,
        groups: ["gruppe1, gruppe2"],
        date: "2024-12-24",
        showDialog: true,
      },
    });

    expect(wrapper.props().stopHour).toBe(8); // Make sure the component is mounted
    expect(wrapper.props().groups).toStrictEqual(["gruppe1, gruppe2"]);
    expect(wrapper.props().date).toBe("2024-12-24"); // Make sure the component is mounted
    expect(wrapper.props().showDialog).toBe(true); // Make sure the component is mounted

    // Make sure the component is mounted
  });
});
