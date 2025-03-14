<template>
  <v-card class="mx-2 my-2" width="425" elevation="16">
    <v-card-item>
      <div class="d-flex justify-space-between align-center">
        <v-card-title class="mb-2">{{ props.name }}</v-card-title>
        <v-chip color="primary" density="comfortable">{{
          props.group_number
        }}</v-chip>
      </div>
      <v-card-subtitle>
        <v-icon color="primary" icon="mdi-account-circle" size="small"></v-icon>
        <span class="me-1 ml-2"
          >{{ props.group_leader.first_name }}
          {{ props.group_leader.last_name }}</span
        >
      </v-card-subtitle>
    </v-card-item>
    <v-card-text>
      <v-divider></v-divider>
      <div class="mt-3 d-flex justify-space-between align-center">
        <v-chip
          prepend-icon="mdi-account-multiple"
          color="primary"
          label
          density="comfortable"
        >
          Mitgliederanzahl: {{ props.employees.length }}
        </v-chip>
        <v-btn
          class="bg-primary"
          @click="openDialog"
          size="default"
          density="comfortable"
          ><v-icon>mdi-information-outline</v-icon></v-btn
        >
      </div>
    </v-card-text>
  </v-card>

  <v-dialog v-model="more" max-width="600" max-height="600" scrollable>
    <v-card>
      <v-card-title color="primary">
        <div class="text-center mt-4">
          <v-chip color="primary" label>
            <p class="text-h5 font-weight-black">{{ props.name }}</p>
          </v-chip>
        </div>
      </v-card-title>
      <div class="mb-2">
        <v-tabs v-model="tab" align-tabs="center" color="primary">
          <v-tab value="one">Übersicht</v-tab>
          <v-tab value="two">Mitglieder</v-tab>
        </v-tabs>
      </div>

      <v-card-text>
        <v-tabs-window v-model="tab">
          <v-tabs-window-item value="one">
            <div class="text-left ml-4 mb-2 mt-2">
              <p class="font-weight-black">Gruppe</p>
            </div>
            <div class="ml-5 mb-4 text-medium-emphasis">
              <p color="text-primary">
                Gruppennummer: {{ props.group_number }}
              </p>
              <p color="text-primary">
                Mitgliederanzahl: {{ props.employees.length }}
              </p>
            </div>
            <v-divider></v-divider>
            <div class="text-left ml-4 mb-2 mt-4">
              <p class="font-weight-black">Gruppenleitung</p>
            </div>
            <div class="ml-5 text-medium-emphasis">
              <p color="text-primary">
                Vorname: {{ props.group_leader.first_name }}
              </p>
              <p color="text-primary">
                Nachname: {{ props.group_leader.last_name }}
              </p>
              <p color="text-primary">
                Benutzername: {{ props.group_leader.username }}
              </p>
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
            <v-data-table-virtual
              :items="props.employees"
              :search="search"
              :headers="headers"
              :sort-by="sortBy"
              :hover="true"
              density="compact"
            >
            </v-data-table-virtual>
          </v-tabs-window-item>
        </v-tabs-window>
      </v-card-text>
      <v-card-actions>
        <div class="d-flex justify-end ga-1">
          <v-btn class="mt-2 bg-primary" @click="closeDialog"
            ><v-icon>mdi-close-thick</v-icon></v-btn
          >
        </div>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
const props = defineProps([
  "group_number",
  "id",
  "name",
  "group_leader",
  "group_leader_replacement",
  "employees",
]);
const more = ref(false);
const tab = ref("");
const search = ref("");

const headers = [
  { title: "Nummer", key: "employee_number" },
  { title: "Nachname", key: "last_name" },
  { title: "Vorname", key: "first_name" },
];

const sortBy = [{ key: "employee_number", order: "asc" }];

const openDialog = () => {
  more.value = true;
};

const closeDialog = () => {
  more.value = false;
};
</script>
