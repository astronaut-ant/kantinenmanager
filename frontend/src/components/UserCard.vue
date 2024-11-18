<template>
  <v-card class="mx-4 my-4" elevation="16" min-width="20em">
    <v-card-item>
      <div class="d-flex justify-space-between">
        <v-card-title>{{ props.name }}</v-card-title>
        <v-chip color="primary" label> #{{ props.id }}</v-chip>
      </div>
      <v-card-subtitle>{{ formattedRole }} </v-card-subtitle>
      <div class="mt-5 d-flex ga-1 justify-end">
        <v-btn class="mt-2 bg-primary"><v-icon>mdi-lead-pencil</v-icon></v-btn>
        <v-btn class="mt-2 bg-red"
          ><v-icon>mdi-trash-can-outline</v-icon></v-btn
        >
      </div>
    </v-card-item>
  </v-card>
</template>

<script setup>
const props = defineProps(["id", "name", "role"]);
const formattedRole = computed(() => {
  let capitalized = props.role.charAt(0).toUpperCase() + props.role.slice(1);
  return capitalized.replace("ue", "ü");
});
</script>
