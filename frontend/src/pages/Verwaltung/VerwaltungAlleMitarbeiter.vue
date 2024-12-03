<template>
  <NavbarVerwaltung />
  <v-container max-width="1000">
    <div>
      <v-toolbar color="white" flat dark>
        <p class="text-h5 font-weight-black" >Übersicht Mitarbeiter</p>
        <v-spacer></v-spacer>
        <v-btn icon="mdi-magnify" @click="toggleSearchField"></v-btn>
        <v-btn icon="mdi-reload"></v-btn>
      </v-toolbar>
    </div>
    <div class="d-flex justify-center">
      <v-expand-transition>
        <v-text-field
        v-if="isSearchVisible"
        v-model="search"
        density="compact"
        label="Suche"
        prepend-inner-icon="mdi-magnify"
        variant="solo-filled"
        flat
        hide-details
        single-line
        clearable
        rounded
        max-width="800"
        ></v-text-field>
      </v-expand-transition>
    </div>
    <div>
      <v-data-table :headers="headers"  :items="items" :search="search">
      <template v-slot:[`item.actions`]="{ item }">
        <v-btn icon="mdi-qrcode" class="bg-green mr-2" @click="openDialog(item)" size="small"></v-btn>
        <v-btn icon="mdi-lead-pencil" class="bg-primary mr-2" @click="openDialog(item)" size="small"></v-btn>
        <v-btn icon="mdi-trash-can-outline" class="bg-red" @click="opendeleteDialog(item)" size="small"></v-btn>
      </template>
      </v-data-table>
    </div>
  </v-container>
  <v-dialog v-model="deleteDialog" persistent max-width="400">
    <v-card>
      <v-card-text>
        <div class="d-flex justify-center text-red mb-4">
          <p class="text-h5 font-weight-black" >Mitarbeiter löschen</p>
        </div>
        <div class="text-medium-emphasis">
          <p> Sind Sie sicher, dass Sie den Mitarbeiter <strong>{{ employeeToDelete }}</strong> löschen möchten?</p>
        </div>
      </v-card-text>
      <v-card-actions>
        <v-btn text @click="closedeleteDialog">Abbrechen</v-btn>
        <v-btn color="red" variant="elevated" @click="confirmDelete">Löschen</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
 
 
<script setup>
  const search = ref("");
  const isSearchVisible = ref(false);
  const deleteDialog = ref(false);
  const employeeToDelete = ref("");
  const toggleSearchField = () => {
    if (isSearchVisible.value) {
      search.value = "";
    }
    isSearchVisible.value = !isSearchVisible.value;
  };

  const opendeleteDialog = (item) => {
    employeeToDelete.value = item.lastname + ", " + item.firstname;
    deleteDialog.value= true;
  };

  const closedeleteDialog = () => {
    deleteDialog.value = false;
  };


  const items = ref([
     {
         employee_number: 0,
         lastname: 'Müller',
         firstname: 'Max',
         group: 'Berufsbildungsbereich 1 - W1',
         location: 'W8',
         ID: 'GWUGDWUAG'
     },
     {
         employee_number: 1,
         lastname: 'Schmidt',
         firstname: 'Lisa',
         group: 'Stanzanlage/Spritzgußmaschine - Zedtlitz',
         location: 'Zedtlitz',
         ID: 'uiawduiogawui'
     },
  ]);
 
 
  const headers = ref([
     { title: "Nummer", key: "employee_number" },
     { title: "Nachname", key: "lastname" },
     { title: "Vorname", key: "firstname" },
     { title: "Gruppe", key: "group" },
     { title: "Standort", key: "location"},
     { title: "", key: "actions", sortable: false },]);
</script>
 