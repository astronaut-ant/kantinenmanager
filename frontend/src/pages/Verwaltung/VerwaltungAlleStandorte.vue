<template>
  <NavbarVerwaltung />
  <FilterBar
    :viewSwitcherEnabled="false"
    :filterList="['location_name', 'location_leader.first_name', 'location_leader.last_name']"
    :items="filterlocationsWithGroups"
    @searchresult="updateOverview"
  />
  <GridContainer :items="locationsWithGroups">
      <template #default="{ item }">
          <LocationCard
              :id="item.id"
              :location_name="item.location_name"
              :location_leader="item.location_leader"
              :groups="item.groups"
              @location-edited="fetchData"
              @location-removed="fetchData"
          />
      </template>
  </GridContainer>
</template>

<script setup>
import FilterBar from "@/components/SearchComponents/FilterBar.vue";
import axios from "axios";
const locations = ref([]);
const locationgroups = ref([]);
const locationsWithGroups = ref([]);
const filterlocationsWithGroups = ref([]);

const fetchData = () => {
  axios
    .get(import.meta.env.VITE_API + "/api/locations", { withCredentials: true })
    .then((response) => {
      locations.value = Object.values(response.data);
      console.log("Locations:", locations.value);

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

const updateOverview = (items) => {
  locationsWithGroups.value = items;
};

onMounted(() => {
  fetchData();
});

</script>