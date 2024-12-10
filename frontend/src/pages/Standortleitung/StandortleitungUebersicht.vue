<template>
  <NavbarStandort></NavbarStandort>
  <v-container max-width="1400" class="d-flex justify-center">
    <v-row class="d-flex justify-start">
      <v-col
        v-if="loading"
        v-for="n in 6"
        :key="n"
        cols="12" md="6" lg="4"
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
        v-for="group in enrichedGroups"
        :key="group.id"
        cols="12" md="6" lg="4"
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
  </v-container>
</template>

<script setup>
  import axios from "axios";

  const groups = ref([]);
  const employees = ref([]);
  const enrichedGroups = ref([]);
  const loading = ref(true);

  const fetchData = async () => {
    try {
      const [employeesResponse, groupsResponse] = await Promise.all([
        axios.get("http://localhost:4200/api/employees", { withCredentials: true }),
        axios.get("http://localhost:4200/api/groups", { withCredentials: true }),
      ]);

      employees.value = employeesResponse.data;
      groups.value = groupsResponse.data;

      enrichedGroups.value = groups.value.map((group) => {
        return {
          id: group.id,
          group_name: group.group_name,
          group_leader: group.user_id_group_leader,
          group_leader_replacement: group.user_id_replacement,
          employees: employees.value.filter(emp => emp.group_id === group.id),
        };
      });
      loading.value = false;
    } catch (err) {
      console.error("Error fetching data", err);
    }
  };

  onMounted(() => {
    fetchData();
  });
</script>