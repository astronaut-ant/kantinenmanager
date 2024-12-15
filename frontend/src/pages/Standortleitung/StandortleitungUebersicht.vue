<template>
  <NavbarStandort></NavbarStandort>
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
          v-for="group in groups"
          :key="group.id"
          cols="12" sm="12" md="6" lg="4" xl="3" xxl = "2"
          class="d-flex justify-center"
        >
          <GroupCard
            :id="group.id"
            :name="group.group_name"
            :group_leader="group.group_leader"
            :group_leader_replacement="group.group_leader_replacement"
            :employees="group.employees"
          />
        </v-col>
      </v-row>
    </div>
</template>

<script setup>
  import axios from "axios";

  const groups = ref([]);
  const loading = ref(true);

  const fetchData = () => {
    axios
    .get(import.meta.env.VITE_API + "/api/groups/with-employees", { withCredentials: true })
    .then((response) => {
      groups.value = response.data;
      loading.value = false;
    })
    .catch((err) => console.error("Error fetching data", err));
  };

  onMounted(() => {
    fetchData();
  });
</script>