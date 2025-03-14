<template>
  <NavbarVerwaltung />
  <v-container>
    <v-row justify="center" class="mt-6 mb-4">
      <v-col cols="12" class="text-center">
        <h1 class="text-h4 font-weight-bold">Abrechnung erstellen</h1>
      </v-col>
    </v-row>

    <v-row justify="center" class="align-center">
      <v-col cols="3" class="text-center d-flex align-center justify-end">
        <v-divider class="flex-grow-1 mr-2"></v-divider>
        <v-btn variant="tonal" size="large" :color="selected === 'standort' ? 'primary' : 'black'"
               @click="selected = 'standort'">
          Standort
        </v-btn>
      </v-col>

      <v-col cols="3" class="text-center d-flex align-center justify-center">
        <v-divider class="flex-grow-1 mx-2"></v-divider>
        <v-btn variant="tonal" size="large" :color="selected === 'gruppe' ? 'primary' : 'black'"
               @click="selected = 'gruppe'">
          Gruppe
        </v-btn>
        <v-divider class="flex-grow-1 mx-2"></v-divider>
      </v-col>

      <v-col cols="3" class="text-center d-flex align-center justify-start">
        <v-btn variant="tonal" size="large" :color="selected === 'mitarbeiter' ? 'primary' : 'black'"
               @click="selected = 'mitarbeiter'">
          Mitarbeiter
        </v-btn>
        <v-divider class="flex-grow-1 ml-2"></v-divider>
      </v-col>
    </v-row>

    <v-row justify="center" class="mt-4">
      <v-col cols="6">

        <v-card v-if="selected==='standort'" class="pa-4">
          <v-card-title class="text-h6 text-center">
            Abrechnung für einen Standort
          </v-card-title>
          <v-card-text>
            Standort für welchen die Abrechnung erstellt werden soll auswählen.
            <v-menu>
              <template #activator="{ props }">
                <v-text-field
                  class="mt-1"
                  v-bind="props"
                  v-model="selectedLocationName"
                  label="Standort auswählen"
                  readonly
                  append-inner-icon="mdi-chevron-down"
                  :rules="[required]"
                ></v-text-field>
              </template>
              <v-list>
                <v-list-item
                  v-for="location in locations"
                  :key="location.id"
                  @click="selectLocation(location)"
                >
                  <v-list-item-title>
                    {{ location?.location_name }}
                  </v-list-item-title>
                </v-list-item>
              </v-list>
            </v-menu>
            <v-menu v-model="dateMenu1" location="center" transition="scale-transition">
              <template v-slot:activator="{ props }">
                <v-text-field
                  v-model="selectedMonthFormatted"
                  label="Monat auswählen"
                  readonly
                  v-bind="props"
                  append-inner-icon="mdi-chevron-down"
                  :rules="[required]"
                ></v-text-field>
              </template>

              <v-list>
                <v-list-item
                  v-for="month in lastSixMonths"
                  :key="month.value"
                  @click="selectMonth(month)"
                >
                  <v-list-item-title>{{ month.label }}</v-list-item-title>
                </v-list-item>
              </v-list>
            </v-menu>
          </v-card-text>
          <v-card-actions class="justify-center">
            <v-btn
              color="primary"
              variant="elevated"
              :disabled="!selectedLocation || !selectedMonth"
              @click="generateInvoice()"
            >
              Erstellen
            </v-btn>
          </v-card-actions>
        </v-card>

        <v-card v-if="selected==='gruppe'" class="pa-4">
          <v-card-title class="text-h6 text-center">
            Abrechnung für eine Gruppe
          </v-card-title>
          <v-card-text>
            Gruppe für welche die Abrechnung erstellt werden soll auswählen.
            <v-menu offset-y>
              <template #activator="{props}">
                <v-text-field
                  class="mt-1"
                  v-bind="props"
                  v-model="selectedGroupName"
                  label="Gruppe auswählen"
                  readonly
                  append-inner-icon="mdi-chevron-down"
                  :rules="[required]"
                ></v-text-field>
              </template>
              <v-list>
                <v-list-item v-for="location in locations" :key="location.id">
                  <v-list-item-title>{{ location?.location_name }}</v-list-item-title>

                  <template v-slot:append>
                    <v-icon icon="mdi-menu-right" size="x-small"></v-icon>
                  </template>

                  <v-menu
                    offset-y
                    activator="parent"
                    open-on-hover
                    close-on-content-click
                    location="end"
                  >
                    <v-list>
                      <v-list-item
                        v-for="group in getGroupsByLocation(location.id)"
                        :key="group.id"
                        @click="selectGroup(group)"
                      >
                        <v-list-item-title>{{ group.group_name }}</v-list-item-title>
                      </v-list-item>
                      <v-list-item v-if="getGroupsByLocation(location.id).length === 0">
                        <v-list-item-title style="color: red;">Besitzt keine Gruppen!</v-list-item-title>
                      </v-list-item>
                    </v-list>
                  </v-menu>
                </v-list-item>
              </v-list>
            </v-menu>
            <v-menu v-model="dateMenu2" location="center" transition="scale-transition">
              <template v-slot:activator="{ props }">
                <v-text-field
                  v-model="selectedMonthFormatted"
                  label="Monat auswählen"
                  readonly
                  v-bind="props"
                  append-inner-icon="mdi-chevron-down"
                  :rules="[required]"
                ></v-text-field>
              </template>

              <v-list>
                <v-list-item
                  v-for="month in lastSixMonths"
                  :key="month.value"
                  @click="selectMonth(month)"
                >
                  <v-list-item-title>{{ month.label }}</v-list-item-title>
                </v-list-item>
              </v-list>
            </v-menu>
          </v-card-text>
          <v-card-actions class="justify-center">
            <v-btn
              color="primary"
              variant="elevated"
              :disabled="!selectedGroup || !selectedMonth"
              @click="generateInvoice()"
            >
              Erstellen
            </v-btn>
          </v-card-actions>
        </v-card>

        <v-card v-if="selected==='mitarbeiter'" class="pa-4">
          <v-card-title class="text-h6 text-center">
            Abrechnung für einen Mitarbeiter
          </v-card-title>
          <v-card-text>
            Mitarbeiter für welchen eine Abrechnung erstellt werden soll auswählen.
            <v-text-field
              v-model="selectedPersonName"
              class="mt-1"
              label="Mitarbeiter auswählen"
              readonly
              append-inner-icon="mdi-chevron-down"
              @click="personDialog=true"
              :rules="[required]"
            ></v-text-field>
            <v-menu v-model="dateMenu3" location="center" transition="scale-transition">
              <template v-slot:activator="{ props }">
                <v-text-field
                  v-model="selectedMonthFormatted"
                  label="Monat auswählen"
                  readonly
                  v-bind="props"
                  append-inner-icon="mdi-chevron-down"
                  :rules="[required]"
                ></v-text-field>
              </template>

              <v-list>
                <v-list-item
                  v-for="month in lastSixMonths"
                  :key="month.value"
                  @click="selectMonth(month)"
                >
                  <v-list-item-title>{{ month.label }}</v-list-item-title>
                </v-list-item>
              </v-list>
            </v-menu>
          </v-card-text>
          <v-card-actions class="justify-center">
            <v-btn
              color="primary"
              variant="elevated"
              :disabled="!selectedPersonId || selectedPersonId.length < 1 || !selectedMonth"
              @click="generateInvoice()"
            >
              Erstellen
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>

  <v-dialog v-model="personDialog" max-width="800">
    <v-card>
      <div>
        <v-toolbar color="white" flat dark>
          <p class="text-h5 font-weight-black ml-4" >Mitarbeiter Auswahl</p>
          <v-spacer></v-spacer>
          <v-btn icon="mdi-magnify" @click="toggleSearchField"></v-btn>
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
          ></v-text-field>
        </v-expand-transition>
      </div>
      <v-card-text>
        <v-data-table
          :headers="headers"
          :items="items"
          :search="search"
          item-value="id"
          v-model="selectedPersonId"
          show-select
          select-strategy="single"
          dense
          hover
        >
        </v-data-table>
      </v-card-text>
      <v-card-actions class="justify-center">
        <v-btn color="grey darken-1" variant="text" @click="personDialog = false">
          Schließen
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import axios from "axios";
const selected = ref("");
const selectedMonth = ref(null);
const selectedLocation = ref(null);
const selectedLocationName = ref(null);
const locations = ref([]);
const selectedGroup = ref(null);
const selectedGroupName = ref(null);
const groups = ref([]);
const selectedPersonName = ref(null);
const selectedPersonId = ref(null);
const employees = ref([]);
const users = ref([]);
const items = ref([]);
const dateMenu1 = ref(false);
const dateMenu2 = ref(false);
const dateMenu3 = ref(false);
const personDialog = ref(false);
const isSearchVisible = ref(false);
const search = ref("");

const headers = [
     { titel: "Tätigkeit", key: "tätikeit", nowrap: true},
     { title: "Vorname", key: "first_name", nowrap: true },
     { title: "Nachname", key: "last_name", nowrap: true },
     { title: "Standort", key: "location_name", nowrap: true},
     { title: "Gruppe", key: "group_name", nowrap: true },
  ];

const toggleSearchField = () => {
  if (isSearchVisible.value) {
    search.value = "";
  }
  isSearchVisible.value = !isSearchVisible.value;
};

const lastSixMonths = computed(() => {
  const months = [];
  const monthNames = [
    "Januar", "Februar", "März", "April", "Mai", "Juni",
    "Juli", "August", "September", "Oktober", "November", "Dezember"
  ];

  const today = new Date();
  for (let i = 1; i <= 6; i++) {
    const date = new Date(today.getFullYear(), today.getMonth() - i, 1);
    const monthLabel = `${monthNames[date.getMonth()]} ${date.getFullYear()}`;
    const monthValue = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}`;

    months.push({ label: monthLabel, value: monthValue });
  }
  return months;
});

const selectedMonthFormatted = computed(() => {
  return selectedMonth.value
    ? lastSixMonths.value.find(m => m.value === selectedMonth.value)?.label
    : null;
});

const selectMonth = (month) => {
  selectedMonth.value = month.value;
};

const selectLocation = (location) => {
  selectedLocation.value = location;
  selectedLocationName.value = location.location_name;
};

const selectGroup = (group) => {
  selectedGroup.value = group;
  selectedGroupName.value = group.group_name;
};

const required = (v) => {
  return !!v || "Eingabe erforderlich";
};

const getGroupsByLocation = (locationId) => {
  return groups.value.filter((group) => group.location?.id === locationId);
};

const setItems = () => {
  items.value = [
    ...employees.value.map((employee) => ({
      id: employee.id,
      first_name: employee.first_name,
      last_name: employee.last_name,
      group_id: employee.group.id,
      group_name: employee.group.group_name || "Unbekannt",
      location_id: employee.group.location.id || null,
      location_name: employee.group.location.location_name,
      tätikeit: "Gruppenmitglied"
    })),
    ...users.value.map((user) => ({
      id: user.id,
      first_name: user.first_name,
      last_name: user.last_name,
      group_id: null,
      group_name: "-",
      location_id: user.location_id || null,
      location_name: "-",
      tätikeit:
        user.user_group === "kuechenpersonal"
          ? "Küchenpersonal"
          : user.user_group === "verwaltung"
          ? "Verwaltung"
          : user.user_group === "gruppenleitung"
          ? "Gruppenleitung"
          : user.user_group === "standortleitung"
          ? "Standortleitung"
          : user.user_group
    }))
  ];
}

watch(selectedPersonId, (newId) => {
  if (newId) {
    const person = items.value.find(item => item.id === newId[0]);
    selectedPersonName.value = person ? `${person.first_name} ${person.last_name}` : null;
  } else {
    selectedPersonName.value = null;
  }
});

const generateInvoice = () => {
  let id = null;
  let idName = null;

  if (selected.value === "standort") {
    id = selectedLocation.value?.id;
    idName = "location-id";
  } else if (selected.value === "gruppe") {
    id = selectedGroup.value?.id;
    idName = "group-id";
  } else if (selected.value === "mitarbeiter") {
    id = selectedPersonId?.value[0];
    idName = "person-id";
  }

  const startDate = `${selectedMonth.value}-01`;
  const [year, month] = selectedMonth.value.split("-").map(Number);
  const lastDay = new Date(year, month, 0).getDate();
  const endDate = `${selectedMonth.value}-${String(lastDay).padStart(2, "0")}`;

  console.log("Selected:", selected.value);
  console.log("ID:", id);
  console.log("ID-Name:", idName);
  console.log("Startdatum:", startDate);
  console.log("Enddatum:", endDate);

  axios
    .get(
      import.meta.env.VITE_API + "/api/invoices", {
      params: {
        [idName]: id,
        "date-start": startDate,
        "date-end": endDate,
      },
      withCredentials: true,
      responseType: "blob",
    }
    )
    .then((response) => {
      console.log(response.data);
      const blob = new Blob([response.data], { type: "application/pdf" });
      const url = URL.createObjectURL(blob);

      const link = document.createElement("a");
      link.href = url;

      const contentDisposition = response.headers["content-disposition"];
      let filename = "rechnung.pdf";

      if (contentDisposition) {
        const match = contentDisposition.match(/filename="?([^"]+)"?/);
        if (match && match[1]) {
          filename = match[1];
        }
      }

      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      URL.revokeObjectURL(url);
    })
    .catch((err) => {
      console.log(err.response.data.description)
    })
};

onMounted(() => {
  axios
    .get(import.meta.env.VITE_API + "/api/locations", { withCredentials: true })
    .then((response) => {
      locations.value = response.data;
    })
    .catch((err) => console.log(err));
  axios
    .get(import.meta.env.VITE_API + "/api/groups", {
      withCredentials: true,
    })
    .then((response) => {
      groups.value = response.data;
    })
    .catch((err) => console.log(err));
  axios
    .get(import.meta.env.VITE_API + "/api/employees", { withCredentials: true })
    .then((response) => {
      employees.value = response.data;
      setItems();
    })
    .catch((err) => console.log(err));
  axios
    .get(import.meta.env.VITE_API + "/api/users", { withCredentials: true })
    .then((response) => {
      users.value = response.data;
      setItems();
    })
    .catch((err) => console.log(err));
});

</script>
