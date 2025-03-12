<template>
    <v-sheet color="white" style="position: sticky; top: 0px; z-index: 10; padding-top: 2px; padding-bottom: 2px;" >
        <div class="d-flex justify-center align-center mt-4" >
            <v-toolbar class="border" color="white" density="comfortable" style="width: 50%;" rounded="lg" floating >
            <div v-if="props.viewSwitcherEnabled" class="d-flex align-center flex-column ml-6 mr-6">
              <v-btn-toggle
                v-model="ansicht"
                base-color="blue-grey"
                color="primary"
                variant="outlined"
                mandatory
                divided
                density="comfortable"
                @update:modelValue="onToggleChange"
              >
                <v-btn icon="mdi-table-account" value="cardview"></v-btn>
                <v-btn icon="mdi-text-account" value="tableview"></v-btn>
              </v-btn-toggle>
            </div>
            <v-divider v-if="props.viewSwitcherEnabled" inset vertical></v-divider>
            <v-text-field
                base-color="blue-grey"
                class="ml-6 mr-6"
                v-model="search"
                density="compact"
                label="Suche"
                prepend-inner-icon="mdi-magnify"
                variant="solo-filled"
                flat
                hide-details
                single-line
                clearable
                rounded="xl"
            ></v-text-field>
            </v-toolbar>
        </div>
        <div class="mt-4 mb-2 d-flex justify-center align-center">
            <slot name="outside"></slot>
        </div>
    </v-sheet>
  </template>
  
  <script setup>
  import { ref } from "vue";

const props = defineProps(["items", "viewSwitcherEnabled", "filterList"]);
const emit = defineEmits(["searchresult", "changeview"]);

  const ansicht = ref("cardview");
  const search = ref("");
  

const normalizedItems = computed(() =>
  Array.isArray(props.items) ? props.items : Object.values(props.items)
);

const getNestedValue = (obj, path) => {
  return path.split(".").reduce((acc, part) => acc?.[part], obj);
};

const filterItems = () => {
  if (!search.value || !search.value.trim()) return normalizedItems.value;
  return normalizedItems.value.filter((item) =>
    props.filterList.some((key) => {
      const val = getNestedValue(item, key);
      return val?.toString().toLowerCase().includes(search.value.toLowerCase());
    })
  );
};

watch(search, () => {
  emit("searchresult", filterItems());
});

  const onToggleChange = (newValue) => {
    emit("changeview", newValue);
  };
  </script>
  