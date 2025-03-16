import { mount } from "@vue/test-utils";
import UserTable from "../src/components/UserTable.vue";

describe("UserTable", () => {
  it("mounts correct with props", () => {
    const wrapper = mount(Foo, {
      propsData: {
        users: [1, 2],
      },
    });
    expect(wrapper.props().users).toBe([1, 2]);
  });
});
