<template>
    <v-card class="mx-2 my-2" width="450" elevation="16">
        <v-card-item class="mb-1">
            <div class="d-flex justify-space-between align-center">
                <div>
                    <v-card-title>Herr Sebastian Müller</v-card-title>
                    <v-card-subtitle>
                        <v-icon
                        color="primary"
                        icon="mdi-account-group"
                        size="small"
                        ></v-icon>
                        <span class="me-1 ml-2">Hauptgruppe: Montage / Blahblah W1</span>
                    </v-card-subtitle>
                </div>
                
                <v-chip
                    :color="anwesend ? 'green' : 'red'"
                    class="text-uppercase"
                    size="small"
                    label
                >
                    <v-icon class="me-2" v-if="anwesend">mdi-calendar-check-outline</v-icon>
                    <v-icon class="me-2" v-else>mdi-calendar-remove-outline</v-icon>
                    {{ anwesend ? 'präsent' : 'abwesend' }}
                </v-chip>
            </div>
            
        </v-card-item>
        <v-card-text>
            <v-divider></v-divider>
            <div class="mt-3 d-flex justify-space-between align-center">
                <v-chip prepend-icon="mdi-bookmark-off" color="primary" label density="compact"> Keine Vertretung </v-chip>
                <v-btn class="bg-primary" @click="openDialog" size="small">Als Abwesend markieren</v-btn>
            </div>
        </v-card-text>
    </v-card>



</template>
    

<script setup>
const anwesend = ref(true);



</script>