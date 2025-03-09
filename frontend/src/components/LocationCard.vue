<template>
    <v-card class="mx-2 my-2" width="425" elevation="16">
        <v-card-item>
            <v-card-title>{{ location_name }}</v-card-title>
            <v-card-subtitle>
                <v-icon color="primary" icon="mdi-account-circle" size="small"></v-icon>
                <span class="me-1 ml-2">{{ props.location_leader.first_name }} {{ props.location_leader.last_name }}</span>
            </v-card-subtitle>
            <li v-for="group in groups">{{ group }}</li>
        </v-card-item>
        <v-card-text>
            <v-divider></v-divider>
            <div class="mt-3 d-flex justify-space-between align-center">
                <v-chip prepend-icon="mdi-account-multiple" color="primary" label density="comfortable"> Gruppenanzahl: {{props.groups.length}} </v-chip>
                <div class="d-flex ga-1 justify-end">
                    <v-btn class="bg-primary mx-1" @click="openEditDialog(group)" size="default" density="comfortable"><v-icon>mdi-lead-pencil</v-icon></v-btn>
                    <v-btn class="bg-red" @click="handleDelete(group)" size="default" density="comfortable"><v-icon>mdi-trash-can-outline</v-icon></v-btn>
                </div>
            </div>
        </v-card-text>
    </v-card>
</template>

<script setup>
const props = defineProps(["id", "location_name", "location_leader", "groups" ])

</script>