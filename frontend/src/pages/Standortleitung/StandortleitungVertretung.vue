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
          @replacement-set="fetchData2"
          @replacement-removed="fetchData2"
        ></GroupLeaderCard>
      </template>
  </GridContainer>
</template>
  
<script setup>
  import axios from "axios";
  const groupLeaders = ref([]);
  const availableLeaders = ref([]);

  const fetchData = () => {
    groupLeaders.value=[];
    axios
      .get(import.meta.env.VITE_API + "/api/groups", { withCredentials: true })
      .then((response) => {
        const groups = response.data;  
        let availableLeaders = []; 

        groups.forEach((group) => {
          if (!group.group_leader_replacement) {
            availableLeaders.push({
              id: group.group_leader.id,
              name: `${group.group_leader.first_name} ${group.group_leader.last_name}`,
              group_number: group.group_number,
              group: {
                id: group.id,
                name: group.group_name,
                location: group.location,
              },
            });
          }
      });


        availableLeaders = availableLeaders.filter(
          (leader, index, self) =>
            index === self.findIndex((l) => l.id === leader.id)
        );


        groups.forEach((group) => {
          const replacingGroups = groups.filter(
            (g) => g.group_leader_replacement?.id === group.group_leader.id
          );

          groupLeaders.value.push({
            ...group,
            available: !group.group_leader_replacement, 
            replacing_group: replacingGroups.map((replacingGroup) => ({
              id: replacingGroup.id,
              name: replacingGroup.group_name,
              location: replacingGroup.location,
            })),
            available_group_leaders: availableLeaders,
          });
        });

        groupLeaders.value.sort((a, b) => {
          if (!a.available && b.available) return -1;
          if (a.available && !b.available) return 1;

          return a.group_name.localeCompare(b.group_name);
        });
        
      })
      .catch((err) => console.error("Error fetching data", err));
  };

  const fetchData2 = () => {
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
    fetchData2();
  });
</script>
  