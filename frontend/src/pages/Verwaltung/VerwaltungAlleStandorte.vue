<template>
  <NavbarVerwaltung />
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
import axios from "axios";
const locations = ref([]);
const locationgroups = ref([]);
const locationsWithGroups = ref([]);

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

          console.log("Locations with groups:", locationsWithGroups);
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


onMounted(() => {
  fetchData();
});

</script>