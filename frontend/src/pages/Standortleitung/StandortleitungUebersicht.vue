<template>
  <NavbarStandort></NavbarStandort>
  <v-container max-width="1600" class="d-flex justify-center">
    <div class="d-flex justify-center flex-wrap">
      <GroupCard
        v-for="group in groups"
        :id="group.id"
        :name="group.group_name"
        :group_leader="group.user_id_group_leader"
      />
    </div>
  </v-container>
</template>

<script setup>
  import axios from "axios";
  const groups = ref([]);


  const fetchData = () => {
    axios
      .get("http://localhost:4200/api/groups", { withCredentials: true })
      .then((response) => {
        groups.value = response.data;
      })
      .catch((err) => console.log(err));
  };

  onMounted(() => {
    fetchData();
  });

</script>
