<template>
    <v-card class="mx-2 my-2" width="450" elevation="16">
        <v-card-item>
            <div class="mb-2 d-flex justify-center">
                <v-chip
                    :color="available ? ( replacing_group ? 'orange' : 'green'): 'red'"
                    class="text-uppercase d-flex justify-center flex-grow-1" 
                    size="small"
                    label
                >
                    <v-icon class="me-2" v-if="available && !replacing_group">mdi-calendar-check-outline</v-icon>
                    <v-icon class="me-2" v-else-if="available && replacing_group">mdi-calendar-clock-outline</v-icon>
                    <v-icon class="me-2" v-else>mdi-calendar-remove-outline</v-icon>
                    {{ available ? ( replacing_group ? 'Vertretung für ' + props.replacing_group.name : 'verfügbar'): 'abwesend' }}
                </v-chip>
            </div>
            <div class="d-flex align-center">
                <div>
                    <v-card-title>{{ props.group_leader.first_name }} {{ props.group_leader.last_name }}</v-card-title>
                    <v-card-subtitle>
                        <v-icon
                        color="primary"
                        icon="mdi-account-group"
                        size="small"
                        ></v-icon>
                        <span class="me-1 ml-2">Hauptgruppe: {{ props.group_name }}</span>
                    </v-card-subtitle>
                </div>
            </div>
            
        </v-card-item>
        <v-card-text>
            <v-divider></v-divider>
            <div class="mt-3 d-flex justify-end">
                <v-btn v-if="available" :disabled="replacing_group" color="red" @click="opensetGroupReplacementDialog" size="small" flat variant="outlined">Als Abwesend markieren</v-btn>
                <v-btn v-else color="primary" @click="openremoveGroupReplacementDialog" size="small" flat variant="outlined">Als Anwesend markieren</v-btn>
            </div>
        </v-card-text>
    </v-card>
    <v-dialog v-model="setGroupReplacementDialog" persistent max-width="600">
        <v-card>
            <v-card-text>
                <div class="d-flex justify-center text-primary mb-7">
                <p class="text-h5 font-weight-black" >Vertretung setzen</p>
                </div>
                <div class="text-medium-emphasis mb-7">
                <p> Bitte wählen Sie einen neuen Gruppenleiter, der für die Gruppe <strong>{{ props.group_name }}</strong>  Essensbestellungen übernehmen kann. </p>
                </div>
                <v-select
                    v-model="replacementGroupLeader"
                    :items="trueavailable_group_leaders.value"
                    item-title="name"
                    item-value="id"
                    label="Gruppenleiter"
                ></v-select>
                <v-alert
                    color="red"
                    icon="mdi-alert-outline"
                    text="Der aktuelle Gruppenleiter kann bis zu seiner Rückkehr keine Bestellungen für seine Gruppe vornehmen."
                    density="compact"
                ></v-alert>
            </v-card-text>
            <v-card-actions>
                <v-btn text @click="closesetGroupReplacementDialog">Abbrechen</v-btn>
                <v-btn color="primary" variant="elevated" @click="confirmSetGroupReplacement">Vertretung setzen</v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>

    <v-dialog v-model="removeGroupReplacementDialog" persistent max-width="600">
        <v-card>
            <v-card-text>
                <div class="d-flex justify-center text-primary mb-7">
                <p class="text-h5 font-weight-black" >Vertretung löschen</p>
                </div>
                <div class="text-medium-emphasis">
                <p> Durch das Entfernen der Vertretung kann <strong>{{ props.group_leader.first_name }} {{ props.group_leader.last_name }}</strong> wieder Essensbestellungen für die Gruppe <strong>{{ props.group_name }}</strong> übernehmen.</p>
                </div>

            </v-card-text>
            <v-card-actions>
                <v-btn text @click="closeremoveGroupReplacementDialog">Abbrechen</v-btn>
                <v-btn color="primary" variant="elevated" @click="removeGroupReplacement">Vertretung löschen</v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>

</template>
    

<script setup>
    const replacementGroupLeader = ref("");
    const setGroupReplacementDialog = ref(false);
    const removeGroupReplacementDialog = ref(false);
    const trueavailable_group_leaders = ref([]);
    const props = defineProps(["group_id", "group_name", "location" , "group_leader", "group_leader_replacement", "replacing_group", "available", "available_group_leaders"]);
    const emit = defineEmits(["replacement-set", "replacement-removed"]);

    import axios from "axios";

    trueavailable_group_leaders.value = computed(() => {
        return props.available_group_leaders.filter(
            (leader) => leader.id !== props.group_leader.id
        );
    });


    const removeGroupReplacement = () => {
        axios
        .delete(`http://localhost:4200/api/groups/remove-replacement/${props.group_id}`, { withCredentials: true })
        .then(() => {
            emit("replacement-removed");
            closeremoveGroupReplacementDialog();
        })
        .catch((err) => console.error("Error deleting", err));
    };
    const opensetGroupReplacementDialog = () => {
        setGroupReplacementDialog.value = true;
    };

    const closesetGroupReplacementDialog = () => {
        setGroupReplacementDialog.value = false;
    };

    const openremoveGroupReplacementDialog = () => {
        removeGroupReplacementDialog.value = true;
    };

    const closeremoveGroupReplacementDialog = () => {
        removeGroupReplacementDialog.value = false;
    };
    

    const confirmSetGroupReplacement = () => {
        if (!replacementGroupLeader) {
            console.error("No group leader selected");
            return;
        }
        console.log(replacementGroupLeader.value)
        axios
            .put(`http://localhost:4200/api/groups/${props.group_id}`, 
                {   
                    group_name: props.group_name,
                    location_id: props.location.id,
                    user_id_group_leader: props.group_leader.id,
                    user_id_replacement: replacementGroupLeader.value
                }, { withCredentials: true }
            )
            .then(() => {
                console.log("Replacement set successfully");
                emit("replacement-set");
                closesetGroupReplacementDialog();
            })
            .catch((err) => console.error("Error setting replacement", err));
    };
</script>