<template>
  <NavbarVerwaltung :breadcrumbs = '[{"title": "Benutzer"}, {"title": "Alle Benutzer"}]' />
  <FilterBar
    :viewSwitcherEnabled="true"
    :filterList="['username', 'first_name', 'last_name', 'user_group']"
    :items="users"
    @searchresult="updateOverview"
    @changeview="changeview"
  />
  <div v-if="ansicht == 'cardview' && userlist.length != 0" class="grid-container">
    <div
      v-for="user in userlist"
      :key="user.id"
      class="grid-item"
    >
      <UserCard
        :id="user.id"
        :username="user.username"
        :role="user.user_group"
        :firstName="user.first_name"
        :lastName="user.last_name"
        :location_id="user.location_id"
        @user-edited="fetchData"
        @user-removed="fetchData"
      />
    </div>
  </div>
  <div v-if="ansicht == 'tableview' && userlist.length != 0" class="d-flex justify-center">
    <UserTable
      :users="userlist"
      @user-edited="fetchData"
      @user-removed="fetchData"
    >
    </UserTable>
  </div>
  <NoResult v-if="userlist.length == 0" />
  <ErrorSnackbar
    v-model="errorSnackbar"
    :text="errorSnackbarText"
    @close="errorSnackbar = false"
  ></ErrorSnackbar>
</template>

<script setup>
import axios from "axios";
import FilterBar from "@/components/SearchComponents/FilterBar.vue";
import NoResult from "@/components/SearchComponents/NoResult.vue";

const users = ref({});
const userlist = ref([]);
const ansicht = ref("cardview");
const errorSnackbar = ref(false);
const errorSnackbarText = ref ("");

const allLocations = ref([]);

const fetchData = () => {
  axios
    .get(import.meta.env.VITE_API + "/api/users", { withCredentials: true })
    .then((response) => {
      users.value = response.data;
      userlist.value = Object.values(response.data);
      //console.log(users.value);
    })
    .catch((err) => {
      console.log(err);
      errorSnackbarText.value = "Fehler beim laden der Nutzer!";
      errorSnackbar.value = true;
    });

  axios
    .get(import.meta.env.VITE_API + "/api/locations", { withCredentials: true })
    .then((response) => {
      response.data.forEach((location) => {
        allLocations.value.push(location.location_name);
      });
      //console.log(allLocations.value);
    })
    .catch((err) => console.log(err));

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
