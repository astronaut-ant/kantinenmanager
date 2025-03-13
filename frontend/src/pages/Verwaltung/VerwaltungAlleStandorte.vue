<template>
  <NavbarVerwaltung
    :breadcrumbs="[{ title: 'Standorte' }, { title: 'Alle Standorte' }]"
  />
  <FilterBar
    :viewSwitcherEnabled="false"
    :filterList="[
      'location_name',
      'location_leader.first_name',
      'location_leader.last_name',
    ]"
    :items="filterlocationsWithGroups"
    @searchresult="updateOverview"
  />
  <GridContainer
    v-if="locationsWithGroups.length !== 0"
    :items="locationsWithGroups"
  >
    <template #default="{ item }">
      <LocationCard
        :id="item.id"
        :location_name="item.location_name"
        :location_leader="item.location_leader"
        :groups="item.groups"
        :kitchen="kitchenTable[item.id]"
        @location-edited="fetchData"
        @location-removed="fetchData"
      />
    </template>
  </GridContainer>
  <NoResult
    v-if="
      locationsWithGroups.length === 0 && filterlocationsWithGroups.length !== 0
    "
  />
</template>

<script setup>
import FilterBar from "@/components/SearchComponents/FilterBar.vue";
import NoResult from "@/components/SearchComponents/NoResult.vue";
import axios from "axios";
const locations = ref([]);
const locationgroups = ref([]);
const locationsWithGroups = ref([]);
const filterlocationsWithGroups = ref([]);
const kitchenTable = ref({});

const fetchData = () => {
  axios
    .get(import.meta.env.VITE_API + "/api/locations", { withCredentials: true })
    .then((response) => {
      locations.value = Object.values(response.data);
      console.log("Locations:", locations.value);
      locations.value.sort((a, b) =>
        a.location_name.toLowerCase() > b.location_name.toLowerCase()
          ? 1
          : b.location_name.toLowerCase() > a.location_name.toLowerCase()
          ? -1
          : 0
      );
      console.log("Locations:", locations.value);

      getKitchen();
      axios
        .get(import.meta.env.VITE_API + "/api/groups/with-locations", {
          withCredentials: true,
        })
        .then((groupResponse) => {
          locationgroups.value = groupResponse.data;

          locationsWithGroups.value = locations.value.map((location) => {
            const locationName = location.location_name;
            const groups = locationgroups.value[locationName] || [];

            return {
              ...location,
              groups: groups,
            };
          });

          filterlocationsWithGroups.value = locationsWithGroups.value;
        })
        .catch((err) => {
          console.log("Error fetching groups:", err);
          errorSnackbarText.value = "Fehler beim Laden der Gruppen!";
          errorSnackbar.value = true;
        });
    })
    .catch((err) => {
      console.log("Error fetching locations:", err);
      errorSnackbarText.value = "Fehler beim Laden der Standorte!";
      errorSnackbar.value = true;
    });
};

const getKitchen = () => {
  axios
    .get(
      import.meta.env.VITE_API + "/api/users?user_group_filter=kuechenpersonal",
      { withCredentials: true }
    )
    .then((response) => {
      const allKitchenStaff = response.data;
      locations.value.forEach((location) => {
        kitchenTable.value[location.id] = allKitchenStaff.filter((ks) => {
          return ks.location_id === location.id;
        });
        console.log(kitchenTable.value);
      });
    })
    .catch((err) => {
      console.log(err);
    });
};

const updateOverview = (items) => {
  locationsWithGroups.value = items;
};

onMounted(() => {
  fetchData();
});
</script>
