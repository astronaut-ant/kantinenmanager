<template>
  <NavbarVerwaltung/>
  <h1 class="text-center text-pink">Alle Gruppen</h1>
  <div class="mx-4 my-5 d-flex justify-start flex-wrap">
    <v-card class="mx-4 my-4" elevation="16" min-width="17em" max-width="17em"
      v-for="group in sortedGroups"
      :key="group.id"
    >
      <v-card-item>
        <div>
          <v-card-title>
            <div class="d-flex flex-column">
              <span class="text-h6 font-weight-bold text-truncate">{{ group.name }}</span>
              <span class="text-subtitle-2 text-truncate">Standort: {{ group.area }}</span>
            </div>
          </v-card-title>
        </div>
        <v-card-actions class="justify-end">
          <v-btn class="mt-2 bg-primary"
            @click="showDetails(group)"
          >
            <v-icon>mdi-information-outline</v-icon>
          </v-btn>
          <v-btn class="mt-2 bg-red"
            @click="handleDelete(group)"
          >
            <v-icon>mdi-trash-can-outline</v-icon>
          </v-btn>
        </v-card-actions>
      </v-card-item>
    </v-card>
 </div>
 <v-dialog v-model="detailDialog" persistent max-width="600">
  <v-card>
    <v-card-title>
      <div>
        <v-icon left class="mr-2">mdi-account-group</v-icon>
        <span class="text-h5" style="white-space: normal; word-wrap: break-word;">
          {{ selectedGroup?.name }} - {{ selectedGroup?.area }}
        </span>
      </div>
    </v-card-title>
    <v-card-text>
      <p><strong>Gruppenleiter:</strong> {{ selectedGroup?.leiter }}</p>
      <p><strong>Mitglieder:</strong></p>
      <v-data-table :headers="headers" :items="selectedGroup?.members">
      </v-data-table>
    </v-card-text>
    <v-card-actions>
      <v-btn color="primary" @click="closeDetailDialog">Schließen</v-btn>
    </v-card-actions>
  </v-card>
 </v-dialog>

 <v-dialog v-model="deleteDialog" persistent max-width="600">
  <v-card>
    <v-card-text>
      <div class="d-flex justify-center text-red mb-4">
        <p class="text-h5 font-weight-black" >Gruppe löschen</p>
      </div>
      <div class="text-medium-emphasis">
        <p> Sind Sie sicher, dass Sie die Gruppe <strong>{{ groupToDelete?.name }} - {{ groupToDelete?.area }}</strong> löschen möchten?</p>
      </div>
    </v-card-text>
    <v-card-actions>
      <v-btn text @click="closeDeleteDialog">Abbrechen</v-btn>
      <v-btn color="red" variant="elevated" @click="confirmDelete">Löschen</v-btn>
    </v-card-actions>
  </v-card>
 </v-dialog>
</template>

<script setup>
const detailDialog = ref(false);
const deleteDialog = ref(false);
const selectedGroup = ref(null);
const groupToDelete = ref(null);


const groups = [
  {
    name: "Berufsbildungsbereich 1",
    area: "W1",
    id: 9509,
    leiter: "Hans Friedrich",
    members: [{firstName: "Allice", lastName: "Skywalker", number: 892484},
              {firstName: "Bob", lastName: "Baumeister", number: 23},
              {firstName: "Charlie", lastName: "Sjdjnedo", number: 2083},
              {firstName: "Hallon", lastName: "Maus", number: 3847},
              {firstName: "Charlie", lastName: "Sjdjnedo", number: 2083},
              {firstName: "Charlie", lastName: "Sjdjnedo", number: 2083},
              {firstName: "Charlie", lastName: "Sjdjnedo", number: 2083},
              {firstName: "Charlie", lastName: "Sjdjnedo", number: 2083},
              {firstName: "Charlie", lastName: "Sjdjnedo", number: 2083},
              {firstName: "Charlie", lastName: "Sjdjnedo", number: 2083},
              {firstName: "Charlie", lastName: "Sjdjnedo", number: 2083},
              {firstName: "Charlie", lastName: "Sjdjnedo", number: 2083},
              {firstName: "Charlie", lastName: "Sjdjnedo", number: 2083},
              {firstName: "Charlie", lastName: "Sjdjnedo", number: 2083},
              {firstName: "Charlie", lastName: "Sjdjnedo", number: 2083},
              {firstName: "Charlie", lastName: "Sjdjnedo", number: 2083},],
  },
  {
    name: "Montage/Verpackung 1",
    area: "Zedtlitz",
    id: 1234,
    leiter: "Petra Müller",
    members: ["Diana", "Elias", "Felix"],
  },
  {
    name: "FBB 2 - Gruppe 1",
    area: "W1",
    id: 8472,
    leiter: "Tom Schulz",
    members: ["Gina", "Hanna", "Isabel"],
  },
  {
    name: "Autoaufbereitung",
    area: "Zedtlitz",
    id: 209,
    leiter: "Hans Friedrich",
    members: ["Alice", "Bob", "Charlie"],
  },
  {
    name: "Stanzanlage/Spritzgußmaschine",
    area: "W1kshskdsjdkdsjksjjiopnosrdrddsjdskj",
    id: 9293,
    leiter: "Petra Müller",
    members: ["Diana", "Elias", "Felix"],
  },
  {
    name: "Gruppe 3",
    area: "Zedtlitz",
    id: 98765,
    leiter: "Tom Schulz",
    members: ["Gina", "Hanna", "Isabel"],
  },
  {
    name: "Gruppe 3",
    area: "W1",
    id: 8472,
    leiter: "Tom Schulz",
    members: ["Gina", "Hanna", "Isabel"],
  },
  {
    name: "Gruppe 3",
    area: "W1",
    id: 8472,
    leiter: "Tom Schulz",
    members: ["Gina", "Hanna", "Isabel"],
  },
  {
    name: "Gruppe 3",
    area: "W1",
    id: 8472,
    leiter: "Tom Schulz",
    members: ["Gina", "Hanna", "Isabel"],
  },
  {
    name: "Gruppe 3",
    area: "W1",
    id: 8472,
    leiter: "Tom Schulz",
    members: ["Gina", "Hanna", "Isabel"],
  },
  {
    name: "Gruppe 3",
    area: "W1",
    id: 8472,
    leiter: "Tom Schulz",
    members: ["Gina", "Hanna", "Isabel"],
  },
  {
    name: "Gruppe 3",
    area: "W1",
    id: 8472,
    leiter: "Tom Schulz",
    members: ["Gina", "Hanna", "Isabel"],
  },
  {
    name: "Gruppe 3",
    area: "W1",
    id: 8472,
    leiter: "Tom Schulz",
    members: ["Gina", "Hanna", "Isabel"],
  },
];

const headers = [
  {title: 'Nummer', key: 'number'},
  {title: 'Vorname', key: 'firstName'},
  {title: 'Nachname', key: 'lastName'}
];

const sortedGroups = groups.sort((a, b) => {
  if (a.area < b.area) {return -1;}
  if (a.area > b.area) {return 1;}

  if (a.name < b.name) {return -1;}
  if (a.name > b.name) {return 1;}

  return 0;
});

const showDetails = (group) => {
  selectedGroup.value = group;
  detailDialog.value = true;
};

const closeDetailDialog = () => {
  detailDialog.value = false;
  selectedGroup.value = null;
}

const handleDelete = (group) => {
  groupToDelete.value = group;
  deleteDialog.value = true;
};

const confirmDelete = () => {
  closeDeleteDialog();
}

const closeDeleteDialog = () => {
  deleteDialog.value = false;
  groupToDelete.value = null;
};
</script>
