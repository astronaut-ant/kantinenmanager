<template>
  <NavbarVerwaltung
    :breadcrumbs="[{ title: 'Mitarbeiter' }, { title: 'Neuer Mitarbeiter' }]"
  />
  <v-container class="text-blue-grey-darken-3" max-width="800">
    <div class="mb-10 mt-10">
      <h3 class="title">Manuelles Hinzufügen eines Mitarbeiters</h3>
      <p class="text mt-3 mb-4">
        Fügen Sie einen Mitarbeiter manuell hinzu, indem Sie alle notwendigen
        Informationen direkt in das Formular eingeben.
      </p>
      <v-btn
        color="primary"
        to="/verwaltung/mitarbeiter/neuerMitarbeiterManuell"
        ><v-icon>mdi-arrow-right-thin-circle-outline</v-icon></v-btn
      >
    </div>
    <v-divider></v-divider>
    <div class="mt-8">
      <h3 class="title">Import per CSV</h3>
      <p class="text mt-3 mb-4">
        Laden Sie eine CSV-Datei hoch, um mehrere Mitarbeiter gleichzeitig zu
        importieren. Achten Sie darauf, dass das Format korrekt ist.
      </p>
      <v-btn
        color="primary"
        to="/verwaltung/mitarbeiter/neuerMitarbeiterCsvUpload"
        ><v-icon>mdi-arrow-right-thin-circle-outline</v-icon></v-btn
      >
    </div>
  </v-container>
</template>

<script setup></script>
