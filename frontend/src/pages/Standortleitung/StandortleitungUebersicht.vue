<template>
  <NavbarStandort></NavbarStandort>
  <v-container max-width="1600" class="d-flex justify-center">
    <div class="d-flex justify-center flex-wrap">
      <GroupCard
        v-for="group in enrichedGroups"
        :key="group.id"
        :id="group.id"
        :name="group.group_name"
        :group_leader="group.group_leader"
        :group_leader_replacement="group.group_leader_replacement"
        :employees="group.employees"
      />
    </div>
  </v-container>
</template>

<script setup>
  import axios from "axios";

  const groups = ref([]);
  const employees = ref([]);
  const enrichedGroups = ref([]);

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
    } catch (err) {
      console.error("Error fetching data", err);
    }
  };

  onMounted(() => {
    fetchData();
  });
</script>
