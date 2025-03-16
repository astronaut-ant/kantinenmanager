import { describe, it, expect, beforeEach } from "vitest";
import { mount } from "@vue/test-utils";
import { createPinia } from "pinia";
import { createVuetify } from "vuetify";
import { createApp } from "vue";

import "vuetify/styles"; // Make sure to import Vuetify's styles

import UserCard from "../src/components/UserCard.vue";

describe("UserCard", () => {
  let pinia;
  let vuetify;

  beforeEach(() => {
    // Create a new Pinia instance for each test to avoid state pollution
    pinia = createPinia();
    vuetify = createVuetify();

    // Create a Vue app instance and apply Vuetify and Pinia
    const app = createApp(UserCard);
    app.use(vuetify); // Apply Vuetify to the app
    app.use(pinia); // Apply Pinia to the app
  });

  it("mounts correctly with props", async () => {
    // Now mount the CalendarDialog component directly
    const wrapper = mount(UserCard, {
      global: {
        plugins: [vuetify, pinia], // Pass the vuetify and pinia plugins to the test mount
      },
      props: {
        id: 1,
        blocked: false,
        username: "test",
        role: "test",
        firstName: "test",
        lastName: "test",
        location_id: 1,
        isFixed: false,
      },
    });

    expect(wrapper.props().id).toBe(1);
    expect(wrapper.props().blocked).toBe(false);
    expect(wrapper.props().username).toBe("test");
    expect(wrapper.props().firstName).toBe("test");
    expect(wrapper.props().lastName).toBe("test");
    expect(wrapper.props().location_id).toBe(1);
    expect(wrapper.props().isFixed).toBe(false);

    // Make sure the component is mounted
  });
});
