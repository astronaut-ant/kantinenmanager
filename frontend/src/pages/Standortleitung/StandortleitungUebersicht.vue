<template>
  <NavbarStandort :breadcrumbs = '[{"title": "Gruppenübersicht"}]'></NavbarStandort>
  <FilterBar 
    :viewSwitcherEnabled="false"
    :filterList="['group_name', 'group_number', 'group_leader.first_name', 'group_leader.last_name', 'group_leader.username']" 
    :items="groups"
    @searchresult="updateOverview"
    @changeview=""
  />

  <GridContainer v-if="grouplist.length !== 0" :items="grouplist">
      <template #default="{ item }">
        <GroupCard
          :group_number="item.group_number"
          :id="item.id"
          :name="item.group_name"
          :group_leader="item.group_leader"
          :group_leader_replacement="item.group_leader_replacement"
          :employees="item.employees"
        />
      </template>
  </GridContainer>
  <NoResult v-if="grouplist.length === 0 && groups.length !== 0" />
</template>

<script setup>
  import FilterBar from "@/components/SearchComponents/FilterBar.vue";
  import NoResult from "@/components/SearchComponents/NoResult.vue";
  import axios from "axios";

  const groups = ref({});
  const grouplist = ref([]);

  const fetchData = () => {
    axios
    .get(import.meta.env.VITE_API + "/api/groups/with-employees", { withCredentials: true })
    .then((response) => {
      groups.value = response.data;
      grouplist.value = Object.values(response.data);
    })
    .catch((err) => console.error("Error fetching data", err));
  };

  onMounted(() => {
    fetchData();
  });

  const updateOverview = (items) => {
    grouplist.value = items;
  };
</script>


<style scoped>

.grid-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(425px, 1fr));
  gap: 10px;
  justify-content: center;
  justify-items: center; 
  padding: 20px;
  width: 100%; 
  max-width: 100%; 
  box-sizing: border-box;
}

.grid-item {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  min-width: 400px;
  max-width: 425px;
}

</style>

