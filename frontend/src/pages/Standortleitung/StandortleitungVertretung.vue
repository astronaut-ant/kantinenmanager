<template>
  <NavbarStandort :breadcrumbs = '[{"title": "Vertretung festlegen"}]'></NavbarStandort>
  <GridContainer :items="groupLeaders">
      <template #default="{ item }">
        <GroupLeaderCard
          :id="item.id"
          :first_name="item.first_name"
          :last_name="item.last_name"
          :own_group="item.own_group"
          :replacement_groups="item.replacement_groups"
          :available_group_leaders="availableLeaders"
          @replacement-set="fetchData"
          @replacement-removed="fetchData"
        ></GroupLeaderCard>
      </template>
  </GridContainer>
</template>
  
<script setup>
  import axios from "axios";
  const groupLeaders = ref([]);
  const availableLeaders = ref([]);

  const fetchData = () => {
    axios
      .get(import.meta.env.VITE_API + "/api/users/group-leaders", { withCredentials: true })
      .then((response) => {
        groupLeaders.value = response.data;
        availableLeaders.value = getAvailableLeaders(groupLeaders.value);

      })
      .catch((err) => console.error("Error fetching data", err));
  };

  const getAvailableLeaders = (leaders) => {
    return leaders
      .filter(leader => leader.own_group.user_id_replacement === null)
      .map(({ id, first_name, last_name }) => ({ id, first_name, last_name, full_name: `${first_name} ${last_name}` })); 
  };

  onMounted(() => {
    fetchData();
  });
</script>
  