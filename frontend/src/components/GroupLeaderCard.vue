<template>
    <v-card class="mx-4 my-4" width="430" elevation="16" min-width="20em" :color="props.anwesend ? 'white' : 'red-lighten-5'">
        <v-card-text>
            <div class="d-flex flex-warp justify-space-between mb-4">
                <div class="text-left ml-1">
                    <p class="text-h6 font-weight-black text-primary"> {{ props.name }} </p>
                </div>
                <div>
                    <v-chip
                        :color="props.anwesend ? 'green' : 'red'"
                        :text="props.anwesend ? 'verfügbar' : 'Nicht verfügbar'"
                        class="text-uppercase"
                        size="small"
                        label>
                    </v-chip>
                </div>
            </div>
            <v-divider></v-divider>
            <div class="d-flex flex-wrap justify-space-between">
                <div class="mt-5 ml-2 text-medium-emphasis">
                    <v-chip color="primary" label> {{ props.group }} </v-chip>
                </div>
                <div class="mt-5 d-flex ga-1">
                    <v-btn 
                    class="mt-2" 
                    :text="props.anwesend ? 'Als Abwesend markieren' : 'Als Anwesend markieren'"
                    @click="openDialog"
                    :color="props.anwesend ? 'red' : 'primary'"
                    ></v-btn>
                </div>
            </div>
        </v-card-text>
    </v-card>
</template>

<script setup>
    const props = defineProps(["id", "name", "loaction" , "group", "anwesend"]);
    const abwesend = ref(false);


</script>