<template>
    <v-breadcrumbs density="comfortable" :items="[{ title: role }, ...breadcrumbs || []]">
        <template v-slot:item="{ item }">
            <v-breadcrumbs-item>
                <span :style="`color: white;`">
                {{ item.title }}
                </span>
            </v-breadcrumbs-item>
        </template>
        <template v-slot:divider>
            <v-icon small >mdi-chevron-right</v-icon>
        </template>
    </v-breadcrumbs>
</template>

<script setup>

const props = defineProps({
    breadcrumbs: {
    type: Array,
    required: false
},
    role: {
    type: String,
    required: true
}
});

</script>