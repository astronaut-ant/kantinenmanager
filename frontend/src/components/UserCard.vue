<template>
  <v-card class="mx-4 my-4 overflow-auto" elevation="16" width="20em">
    <v-card-item>
      <div class="d-flex justify-space-between">
        <v-card-title>{{
          props.firstName + " " + props.lastName
        }}</v-card-title>
        <!-- <v-chip color="primary" label> #{{ props.id }}</v-chip> -->
      </div>
      <v-card-subtitle>{{ props.name }} </v-card-subtitle>
      <v-card-subtitle>{{ formattedRole }} </v-card-subtitle>
      <div class="mt-5 d-flex ga-1 justify-end">
        <v-btn class="mt-2 bg-primary" @click="handleEdit"
          ><v-icon>mdi-lead-pencil</v-icon></v-btn
        >
        <v-btn class="mt-2 bg-red" @click="handleDelete"
          ><v-icon>mdi-trash-can-outline</v-icon></v-btn
        >
      </div>
    </v-card-item>
  </v-card>
</template>

<script setup>
const props = defineProps(["id", "name", "role", "firstName", "lastName"]);
const emit = defineEmits(["delete", "edit"]);
const formattedRole = computed(() => {
  let capitalized = props.role.charAt(0).toUpperCase() + props.role.slice(1);
  return capitalized.replace("ue", "ü");
});

const handleDelete = () => {
  emit("delete", props.id);
};

const handleEdit = () => {
  emit("edit", props.id);
};
</script>
