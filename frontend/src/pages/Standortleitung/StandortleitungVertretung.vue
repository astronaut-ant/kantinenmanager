<template>
  <NavbarStandort
    :breadcrumbs="[{ title: 'Vertretung festlegen' }]"
  ></NavbarStandort>
  <FilterBar
    :viewSwitcherEnabled="false"
    :filterList="['first_name', 'last_name', 'own_group.group_name']"
    :items="originalGroupLeaders"
    @searchresult="updateOverview"
  />
  <GridContainer v-if="groupLeaders.length !== 0" :items="groupLeaders">
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
  <NoResult
    v-if="groupLeaders.length === 0 && originalGroupLeaders.length !== 0"
  />
</template>

<script setup>
import axios from "axios";
import { useAppStore } from "@/stores/app";
const appStore = useAppStore();
const groupLeaders = ref([]);
const originalGroupLeaders = ref([]);
const availableLeaders = ref([]);
const ownLocId = ref(null);
const ownGroups = ref([]);

const fetchData = () => {
  axios
    .get(import.meta.env.VITE_API + "/api/locations", {
      withCredentials: true,
    })
    .then((response) => {
      ownLocId.value = response.data.filter((res) => {
        return res.location_leader.id === appStore.userData.id;
      })[0].id;
      console.log(ownLocId.value);
    })
    .catch((err) => console.error("Error fetching data", err));

  const getGroups = () => {
    axios
      .get(import.meta.env.VITE_API + "/api/groups", {
        withCredentials: true,
      })
      .then((response) => {
        ownGroups.value = response.data;
        console.log(ownGroups);
        let groupIDArray = [];
        ownGroups.value.forEach((group) => {
          groupIDArray.push(group.id);
        });
        console.log(groupIDArray);

        console.log("groups", response.data);
        groupLeaders.value = groupLeaders.value.filter(
          (group) =>
            !group.own_group || groupIDArray.includes(group.own_group.id)
        );
        originalGroupLeaders.value = groupLeaders.value;

        availableLeaders.value = getAvailableLeaders(groupLeaders.value);
      })
      .catch((err) => console.error("Error fetching data", err));
  };

  axios
    .get(import.meta.env.VITE_API + "/api/users/group-leaders", {
      withCredentials: true,
    })
    .then((response) => {
      groupLeaders.value = response.data;
      originalGroupLeaders.value = response.data;
      getGroups();
    })
    .catch((err) => console.error("Error fetching data", err));
};

const getAvailableLeaders = (leaders) => {
  return leaders
    .filter(
      (leader) =>
        leader.own_group === null ||
        leader.own_group.user_id_replacement === null
    )
    .map(({ id, first_name, last_name }) => ({
      id,
      first_name,
      last_name,
      full_name: `${first_name} ${last_name}`,
    }));
};

onMounted(() => {
  fetchData();
});

const updateOverview = (list) => {
  groupLeaders.value = list;
  console.log(list);
};
</script>
