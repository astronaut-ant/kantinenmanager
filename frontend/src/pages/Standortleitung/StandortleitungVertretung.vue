<template>
  <NavbarStandort></NavbarStandort>
  <v-container fluid class="d-flex justify-center">
    <div class="ml-10 mr-10 mt-5">
      <v-row class="d-flex justify-start">
        <v-col
          v-if="loading"
          v-for="n in 6"
          :key="n"
          cols="12" sm="12" md="6" lg="4" xl="3" xxl = "2"
          class="d-flex justify-center"
        >
          <v-skeleton-loader
            class="mx-auto"
            width="400"
            max-height="200"
            type="heading, subtitle, divider, chip"
          />
        </v-col>

        <v-col
          v-else
          v-for="groupLeader in groupLeaders"
          :key="groupLeader.id"
          cols="12" sm="12" md="6" lg="4" xl="3" xxl = "2"
          class="d-flex justify-center"
        >
        <GroupLeaderCard
          :group_id="groupLeader.id"
          :group_name="groupLeader.group_name"
          :location="groupLeader.location"
          :group_leader="groupLeader.group_leader"
          :group_leader_replacement="groupLeader.group_leader_replacement"
          :replacing_group="groupLeader.replacing_group"
          :available="groupLeader.available"
          :available_group_leaders="groupLeader.available_group_leaders"
          @replacement-set="fetchData"
          @replacement-removed="fetchData"
        ></GroupLeaderCard>
        </v-col>
      </v-row>
    </div>
  </v-container>
</template>
  
<script setup>
  import axios from "axios";
  const groupLeaders = ref([]);
  const loading = ref(true);

  const fetchData = () => {
    loading.value=true;
    groupLeaders.value=[];
    axios
      .get("http://localhost:4200/api/groups", { withCredentials: true })
      .then((response) => {
        const groups = response.data;  
        let availableLeaders = []; 

        groups.forEach((group) => {
          const isLeaderAvailable =
            !group.group_leader_replacement &&
            !groups.some(
              (g) => g.group_leader_replacement?.id === group.group_leader.id
            );

          if (isLeaderAvailable) {
            availableLeaders.push({
              id: group.group_leader.id,
              name: `${group.group_leader.first_name} ${group.group_leader.last_name}`,
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
          const replacingGroup = groups.find(
            (g) => g.group_leader_replacement?.id === group.group_leader.id
          );

          groupLeaders.value.push({
            ...group,
            available: !group.group_leader_replacement, 
            replacing_group: replacingGroup
              ? {
                  id: replacingGroup.id,
                  name: replacingGroup.group_name,
                  location: replacingGroup.location,
                }
              : null,
            available_group_leaders: availableLeaders,
          });
        });

        groupLeaders.value.sort((a, b) => {
          if (!a.available && b.available) return -1;
          if (a.available && !b.available) return 1;

          return a.group_name.localeCompare(b.group_name);
        });

        console.log(groupLeaders);
        loading.value = false;
      })
      .catch((err) => console.error("Error fetching data", err));
  };

  onMounted(() => {
    fetchData();
  });
</script>
  