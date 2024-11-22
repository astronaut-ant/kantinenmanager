<template>
  <NavbarVerwaltung />
  <v-container max-width="800">
    <div class="mb-4">
      <h3 class="title">Manuelles Hinzufügen eines Mitarbeiters</h3>
      <p class="text mt-4 mb-4">Fügen Sie einen Mitarbeiter manuell hinzu, indem Sie alle notwendigen Informationen direkt in das Formular eingeben.</p>
      <v-btn color="primary" to="/verwaltung/uebersicht"><v-icon>mdi-arrow-right-thin-circle-outline</v-icon></v-btn>
  </div>
    <v-divider ></v-divider>
    <div class="mt-4">
      <h3 class="title">Import per CSV</h3>
      <p class="text mt-4 mb-4">Laden Sie eine CSV-Datei hoch, um mehrere Mitarbeiter gleichzeitig zu importieren. Achten Sie darauf, dass das Format korrekt ist.</p>
      <v-btn color="primary" to="/verwaltung/behinderung/csv-upload"><v-icon>mdi-arrow-right-thin-circle-outline</v-icon></v-btn>
    </div>
  </v-container>
</template>

<script setup></script>
