import { describe, it, expect, beforeEach } from "vitest";
import { mount } from "@vue/test-utils";
import { createPinia } from "pinia";
import { createVuetify } from "vuetify";
import { createApp } from "vue";

import "vuetify/styles"; // Make sure to import Vuetify's styles

import GroupCard from "../src/components/GroupCard.vue";

describe("LocationCard", () => {
  let pinia;
  let vuetify;

  beforeEach(() => {
    // Create a new Pinia instance for each test to avoid state pollution
    pinia = createPinia();
    vuetify = createVuetify();

    // Create a Vue app instance and apply Vuetify and Pinia
    const app = createApp(GroupCard);
    app.use(vuetify); // Apply Vuetify to the app
    app.use(pinia); // Apply Pinia to the app
  });

  it("mounts correctly with props", async () => {
    // Now mount the CalendarDialog component directly
    const wrapper = mount(GroupCard, {
      global: {
        plugins: [vuetify, pinia], // Pass the vuetify and pinia plugins to the test mount
      },
      props: {
        group_leader: 1234,
        employees: [],
      },
    });

    expect(wrapper.exists()).toBe(true);

    // Make sure the component is mounted
  });
});
