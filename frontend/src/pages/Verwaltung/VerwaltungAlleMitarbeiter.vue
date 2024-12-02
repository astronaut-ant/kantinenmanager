<template>
  <NavbarVerwaltung />
  <v-container max-width="1000">
   <div class="text-center mt-4 mb-10">
     <p class="text-h5 font-weight-black" >Übersicht Mitarbeiter</p>
   </div>
   <div>
     <v-text-field
       v-model="search"
       density="compact"
       label="Suche"
       prepend-inner-icon="mdi-magnify"
       variant="solo-filled"
       flat
       hide-details
       single-line
     ></v-text-field>
     <v-data-table :headers="headers"  :items="items" :search="search">
       <template v-slot:[`item.actions`]="{ item }">
         <v-btn icon="mdi-lead-pencil" class="bg-primary mr-2" @click="openDialog(item)" size="small"></v-btn>
         <v-btn icon="mdi-trash-can-outline" class="bg-red" @click="openDialog(item)" size="small"></v-btn>
       </template>
     </v-data-table>
   </div>
  </v-container>
</template>
 
 
<script setup>
   const search = ref("");
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
 