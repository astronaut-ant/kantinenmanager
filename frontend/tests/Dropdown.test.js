import { describe, it, expect, beforeEach } from "vitest";
import { mount } from "@vue/test-utils";
import { createPinia } from "pinia";
import { createVuetify } from "vuetify";
import { createApp } from "vue";

import "vuetify/styles"; // Make sure to import Vuetify's styles

import Dropdown from "../src/components/Dropdown.vue";

describe("Dropdown", () => {
  let pinia;
  let vuetify;

  beforeEach(() => {
    // Create a new Pinia instance for each test to avoid state pollution
    pinia = createPinia();
    vuetify = createVuetify();

    // Create a Vue app instance and apply Vuetify and Pinia
    const app = createApp(Dropdown);
    app.use(vuetify); // Apply Vuetify to the app
    app.use(pinia); // Apply Pinia to the app
  });

  it("mounts correctly with props", async () => {
    // Now mount the CalendarDialog component directly
    const wrapper = mount(Dropdown, {
      global: {
        plugins: [vuetify, pinia], // Pass the vuetify and pinia plugins to the test mount
      },
      props: {
        items: ["test1", "test2"],
        menuName: "testGericht",
        menuIcon: "testIcon",
      },
    });

    expect(wrapper.props().items).toStrictEqual(["test1", "test2"]); // Make sure the component is mounted
    expect(wrapper.props().menuName).toBe("testGericht"); // Make sure the component is mounted
    expect(wrapper.props().menuIcon).toBe("testIcon"); // Make sure the component is mounted

    // Make sure the component is mounted
  });
});
