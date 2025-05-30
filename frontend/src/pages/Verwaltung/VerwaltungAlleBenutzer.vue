<template>
  <NavbarVerwaltung
    :key="forcer"
    :breadcrumbs="[{ title: 'Benutzer' }, { title: 'Alle Benutzer' }]"
  />
  <FilterBar
    :viewSwitcherEnabled="true"
    :filterList="['username', 'first_name', 'last_name', 'user_group']"
    :items="users"
    @searchresult="updateOverview"
    @changeview="changeview"
  />
  <GridContainer
    v-if="ansicht == 'cardview' && userlist.length !== 0"
    :items="userlist"
  >
    <template #default="{ item }">
      <UserCard
        :id="item.id"
        :blocked="item.blocked"
        :username="item.username"
        :role="item.user_group"
        :firstName="item.first_name"
        :lastName="item.last_name"
        :location_id="item.location_id"
        :isFixed="checkIfFixed(item.id)"
        @user-edited="fetchData"
        @user-removed="fetchData"
        @avatar-changed="reset"
      />
    </template>
  </GridContainer>
  <div
    v-if="ansicht == 'tableview' && userlist.length !== 0"
    class="d-flex justify-center"
  >
    <UserTable
      :users="userlist"
      @user-edited="fetchData"
      @user-removed="fetchData"
    >
    </UserTable>
  </div>
  <NoResult v-if="userlist.length === 0 && users.length !== 0" />
</template>

<script setup>
import axios from "axios";
import FilterBar from "@/components/SearchComponents/FilterBar.vue";
import NoResult from "@/components/SearchComponents/NoResult.vue";
import GridContainer from "@/components/GridContainer.vue";
import { useFeedbackStore } from "@/stores/feedback";

const feedbackStore = useFeedbackStore();
const users = ref({});
const userlist = ref([]);
const ansicht = ref("cardview");
const forcer = ref(1);
const allLocations = ref([]);
const fixedGroupLeaderIDs = ref([]);
const fixedLocationLeaderIDs = ref([]);

const fetchData = () => {
  axios
    .get(import.meta.env.VITE_API + "/api/users", { withCredentials: true })
    .then((response) => {
      users.value = response.data.map(user => {
        let capitalizedRole = user.user_group.charAt(0).toUpperCase() + user.user_group.slice(1);
        user.user_group = capitalizedRole.replace("ue", "ü");
        return user;
      });

      users.value.sort((a, b) =>
        a.username.toLowerCase() > b.username.toLowerCase()
          ? 1
          : b.username.toLowerCase() > a.username.toLowerCase()
          ? -1
          : 0
      );

      userlist.value = Object.values(users.value);

      //console.log(userlist.value);
    })
    .catch((err) => {
      console.error("Error fetching data", err);
      feedbackStore.setFeedback(
        "error",
        "snackbar",
        err.response?.data?.title,
        err.response?.data?.description
      );
    });

  axios
    .get(import.meta.env.VITE_API + "/api/locations", { withCredentials: true })
    .then((response) => {
      response.data.forEach((location) => {
        allLocations.value.push(location.location_name);
        fixedLocationLeaderIDs.value.push(location.location_leader.id);
        axios
          .get(import.meta.env.VITE_API + "/api/groups", {
            withCredentials: true,
          })
          .then((response) => {
            response.data.forEach((group) => {
              fixedGroupLeaderIDs.value.push(group.group_leader.id);
              userlist.value.forEach((user) => {
                user.isFixed = checkIfFixed(user.id);
              });
            });
            console.log("fixed Groupleaders: ", fixedGroupLeaderIDs.value);

            //console.log(allLocations.value);
          })
          .catch((err) => console.log(err));
      });
      console.log("fixed Locationleaders: ", fixedLocationLeaderIDs.value);

      //console.log(allLocations.value);
    })
    .catch((err) => {
      console.error("Error fetching data", err);
      feedbackStore.setFeedback(
        "error",
        "snackbar",
        err.response?.data?.title,
        err.response?.data?.description
      );
    });

  //TODO Fetch actual location for initial selection in v-Select
};

onMounted(() => {
  fetchData();
});

const updateOverview = (items) => {
  userlist.value = items;
};

const changeview = (string) => {
  ansicht.value = string;
};

const reset = () => {
  forcer.value += 1;
  forcer.value %= 2;
};
const checkIfFixed = (id) => {
  return fixedGroupLeaderIDs.value
    .concat(fixedLocationLeaderIDs.value)
    .includes(id);
};
</script>
