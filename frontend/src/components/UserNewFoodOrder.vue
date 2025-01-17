<template>
  <v-dialog v-model="dialog" width="400">
    <template v-slot:activator="{ props: activatorProps }">
      <v-btn v-bind="activatorProps" class="mt-2 mb-5" color="primary">
        <v-icon class="me-2">mdi-plus</v-icon>Neue Bestellung aufgeben
      </v-btn>
    </template>

    <!-- <v-card class="mx-auto px-4" color="blue-grey-lighten-5">
      <v-card-text>
        <h2 class="mt-2 mb-6 text-blue-grey font-weight-bold">
          <v-icon class="me-4 text-blue-grey">
            mdi-calendar-edit-outline</v-icon
          >
          Neue Bestellung aufgeben
        </h2> -->

    <div class="d-flex justify-center">
      <v-stepper
        prev-text="Zurück"
        next-text="Weiter"
        class="test"
        :width="400"
        color="primary"
        elevation="24"
        bg-color="#ECEFF1"
        :items="['Datum', 'Standort', 'Menü']"
      >
        <template v-slot:item.1>
          <v-card
            class="test"
            color="#ECEFF1"
            title="Datum der Bestellung"
            flat
          >
            <v-container>
              <v-row justify="space-around">
                <v-date-picker
                  elevation="2"
                  class="test"
                  height="350"
                  color="primary"
                  bg-color="#ECEFF1"
                  :first-day-of-week="1"
                  :hide-header="true"
                >
                </v-date-picker>
              </v-row>
            </v-container>
          </v-card>
        </template>

        <template v-slot:item.2>
          <v-card color="#ECEFF1" title="Standort der Bestellung" flat>
            <v-select
              bg-color="white"
              color="blue-grey"
              variant="solo"
            ></v-select>
          </v-card>
        </template>

        <template v-slot:item.3>
          <v-card title="Step Three" flat>...</v-card>
        </template>
      </v-stepper>
      <!-- </v-card-text> -->
      <!-- </v-card> -->
    </div>
  </v-dialog>
</template>

<script setup>
const dialog = ref(false);
</script>

<style scoped>
.test {
  color: #607d8b !important;
}
</style>

<style>
.v-stepper-item__avatar.v-avatar {
  background: #1867c0 !important;
}
</style>

<!-- Dummy -->
