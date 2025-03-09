<template>
    <NavbarVerwaltung />
    <div
      v-for="location in locationsWithGroups"
      :key="location.id"
    >
      <LocationCard
        :id="location.id"
        :location_name="location.location_name"
        :location_leader="location.location_leader"
        :groups="location.groups"
      />
    </div>
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