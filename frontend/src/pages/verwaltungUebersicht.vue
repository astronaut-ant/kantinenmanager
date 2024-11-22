<template>
  <NavbarVerwaltung />
  <div class="mx-4 my-5 d-flex justify-start flex-wrap">
    <UserCard
      v-for="user in users"
      :id="user.id"
      :name="user.username"
      :role="user.user_group"
    />
  </div>
</template>

<script setup>
import axios from "axios";
const users = ref({});
onMounted(() => {
  axios
    .get("http://localhost:4200/api/users", { withCredentials: true })
    .then((response) => {
      users.value = response.data;
      console.log(users.value);
    })
    .catch((err) => console.log(err));
});
</script>
