<template>
    <v-card class="mx-4 my-4" width="450" elevation="16" min-width="20em">
        <v-card-text>
            <div class="d-flex flex-warp justify-space-between mb-4">
                <div class="text-left ml-1">
                    <p class="text-h6 font-weight-black text-primary"> {{ props.name }} </p>
                </div>
                <div style="max-width: 100px; overflow: hidden;">
                    <v-chip color="primary" label> {{ props.number }} </v-chip>
                </div>
            </div>
            <v-divider></v-divider>
            <div class="d-flex flex-wrap justify-space-between">
                <div class="mt-4 ml-2 text-medium-emphasis">
                    <p color="text-primary"> Gruppenleiter: {{ props.group_leader }}</p>
                    <p color="text-primary"> Mitgliederanzahl: 99 </p>
                    <p color="text-primary"> Standort: {{ props.loaction }} </p>
                </div>
                <div class="mt-5 d-flex ga-1">
                    <v-btn class="mt-2 bg-primary" @click="openDialog"><v-icon>mdi-dots-horizontal-circle-outline</v-icon></v-btn>
                </div>
            </div>
        </v-card-text>
    </v-card>

    <v-dialog v-model="more" max-width="600" max-height="600" scrollable>
        <v-card>
            <v-card-title color="primary">
                <div class="text-center mt-4">
                    <v-chip color="primary" label> <p class="text-h5 font-weight-black"> {{ props.name }} </p> </v-chip>
                </div>
            </v-card-title>
            <div class="mb-2">
                <v-tabs v-model="tab" align-tabs="center" color="primary">
                    <v-tab value="one">Übersicht</v-tab>
                    <v-tab value="two">Mitglieder</v-tab>
                    <v-tab value="three">--</v-tab>
                </v-tabs>
            </div>

            <v-card-text>
                <v-tabs-window v-model="tab">
                    <v-tabs-window-item value="one">
                    <div class="text-left ml-4 mb-2 mt-2">
                        <p class="font-weight-black"> Gruppe </p>
                    </div>
                    <div class="ml-5 mb-4 text-medium-emphasis">
                        <p color="text-primary"> Gruppennummer: {{ props.number }} </p>
                        <p color="text-primary"> Mitgliederanzahl: 99 </p>
                        <p color="text-primary"> Standort: {{ props.loaction }} </p>
                    </div>
                    <v-divider></v-divider>
                    <div class="text-left ml-4 mb-2 mt-4">
                        <p class="font-weight-black"> Gruppenleitung </p>
                    </div>
                    <div class="ml-5 text-medium-emphasis">
                        <p color="text-primary"> Vorname: Max </p>
                        <p color="text-primary"> Nachname: Mustermann </p>
                        <p color="text-primary"> Benutzername: testtest </p>
                    </div>

                    </v-tabs-window-item>

                    <v-tabs-window-item value="two">
                        <v-text-field
                            v-model="search"
                            density="compact"
                            label="Suche"
                            prepend-inner-icon="mdi-magnify"
                            variant="solo-filled"
                            flat
                            hide-details
                            clearable
                            single-line
                            rounded
                        ></v-text-field>
                        <v-data-table-virtual :items="items" :search="search" density="compact">
                            <template v-slot:item.Essen="{ item }">
                                <div class="text-left">
                                    <v-chip
                                    :color="item.Essen === 'rot' ? 'red' : (item.Essen === 'blau' ? 'blue' : 'gray')"
                                    :text="item.Essen === 'rot' ? 'Rot' : (item.Essen === 'blau' ? 'Blau' : 'kein Essen')"
                                    class="text-uppercase"
                                    size="small"
                                    label
                                    ></v-chip>
                                </div>
                            </template>
                            <template v-slot:item.Salat="{ item }">
                                <v-checkbox-btn
                                    v-model="item.Salat"
                                    readonly
                                    color="success"
                                ></v-checkbox-btn>
                            </template>

                        </v-data-table-virtual>
                    </v-tabs-window-item>

                    <v-tabs-window-item value="three">
                        ---
                    </v-tabs-window-item>
                </v-tabs-window>
            </v-card-text>
            <v-card-actions>
                <div class="d-flex justify-end ga-1">
                    <v-btn class="mt-2 bg-primary" @click="closeDialog"><v-icon>mdi-close-outline</v-icon></v-btn>
                </div>
            </v-card-actions>
        </v-card>
    </v-dialog>
</template>

<script setup>
    const props = defineProps(["id", "name", "loaction" , "group_leader" , "number"]);
    const more = ref(false);
    const tab = ref("");
    const search = ref("");

    const items = [
    {
        Vorname: 'Max',
        Nachname: 'Müller',
        Essen: 'rot',
        Salat: true
    },
    {
        Vorname: 'Lina',
        Nachname: 'Schmidt',
        Essen: 'rot',
        Salat: true
    },
    {
        Vorname: 'Tom',
        Nachname: 'Schneider',
        Essen: '',
        Salat: false
    },
    {
        Vorname: 'Emma',
        Nachname: 'Fischer',
        Essen: 'blau',
        Salat: false
    },
    {
        Vorname: 'John',
        Nachname: 'Weber',
        Essen: 'blau',
        Salat: false
    },
    {
        Vorname: 'Anna',
        Nachname: 'Meyer',
        Essen: 'rot',
        Salat: true
    },
    {
        Vorname: 'Chris',
        Nachname: 'Wagner',
        Essen: '',
        Salat: true
    },
    {
        Vorname: 'Sophia',
        Nachname: 'Becker',
        Essen: 'blau',
        Salat: true
    },
    {
        Vorname: 'Michael',
        Nachname: 'Hoffmann',
        Essen: 'blau',
        Salat: true
    },
    {
        Vorname: 'Isabella',
        Nachname: 'Koch',
        Essen: 'rot',
        Salat: false
    },
    {
        Vorname: 'David',
        Nachname: 'Bauer',
        Essen: 'rot',
        Salat: false
    },
    {
        Vorname: 'Olivia',
        Nachname: 'Richter',
        Essen: 'rot',
        Salat: true
    },
    {
        Vorname: 'Lucas',
        Nachname: 'Klein',
        Essen: 'blau',
        Salat: true
    },
    {
        Vorname: 'Mia',
        Nachname: 'Wolf',
        Essen: 'blau',
        Salat: false
    },
    {
        Vorname: 'Ethan',
        Nachname: 'Scholz',
        Essen: 'rot',
        Salat: false
    },];



    const openDialog = () => {
        more.value = true;
    };

    const closeDialog = () => {
        more.value = false;
    };


</script>