<template>
  <NavbarVerwaltung :breadcrumbs = '[{"title": "Benutzer"}, {"title": "Alle Benutzer"}]' />
  <FilterBar
    :viewSwitcherEnabled="true"
    :filterList="['username', 'first_name', 'last_name', 'user_group']"
    :items="users"
    @searchresult="updateOverview"
    @changeview="changeview"
  />
  <GridContainer v-if="ansicht == 'cardview' && userlist.length !== 0" :items="userlist">
      <template #default="{ item }">
          <UserCard
          :id="item.id"
          :blocked="item.blocked"
          :username="item.username"
          :role="item.user_group"
          :firstName="item.first_name"
          :lastName="item.last_name"
          :location_id="item.location_id"
          @user-edited="fetchData"
          @user-removed="fetchData"
        />
      </template>
  </GridContainer>
  <div v-if="ansicht == 'tableview' && userlist.length !== 0" class="d-flex justify-center">
    <UserTable
      :users="userlist"
      @user-edited="fetchData"
      @user-removed="fetchData"
    >
    </UserTable>
  </div>
  <NoResult v-if="userlist.length === 0 && users.length !== 0 " />
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
import GridContainer from "@/components/GridContainer.vue";

const users = ref({});
const userlist = ref([]);
const ansicht = ref("cardview");
const errorSnackbar = ref(false);
const errorSnackbarText = ref("");

const allLocations = ref([]);

const fetchData = () => {
  axios
    .get(import.meta.env.VITE_API + "/api/users", { withCredentials: true })
    .then((response) => {
      users.value = response.data;
      users.value.sort((a, b) =>
        a.username > b.username ? 1 : b.username > a.username ? -1 : 0
      );
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
