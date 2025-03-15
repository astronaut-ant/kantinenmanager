<template>
  <NavbarVerwaltung
    :breadcrumbs="[{ title: 'Abrechnung' }, { title: 'Abrechnung erstellen' }]"
  />
  <v-container>
    <v-row justify="center" class="mt-6 mb-4">
      <v-col cols="12" class="text-center">
        <h1 class="text-h4 text-primary font-weight-bold">
          <v-icon class="me-2">mdi-invoice-arrow-left-outline</v-icon>
          Abrechnung erstellen
        </h1>
      </v-col>
    </v-row>

    <v-row justify="center" class="align-center">
      <v-col cols="3" class="text-center d-flex align-center justify-end">
        <v-divider class="flex-grow-1 mr-2"></v-divider>
        <v-btn
          variant="tonal"
          size="large"
          :color="selected === 'standort' ? 'primary' : 'blue-grey'"
          @click="(selected = 'standort'), clearGruppe(), clearPerson()"
        >
          Standort
        </v-btn>
      </v-col>

      <v-col cols="3" class="text-center d-flex align-center justify-center">
        <v-divider class="flex-grow-1 mx-2"></v-divider>
        <v-btn
          variant="tonal"
          size="large"
          :color="selected === 'gruppe' ? 'primary' : 'blue-grey'"
          @click="(selected = 'gruppe'), clearStandort(), clearPerson()"
        >
          Gruppe
        </v-btn>
        <v-divider class="flex-grow-1 mx-2"></v-divider>
      </v-col>

      <v-col cols="3" class="text-center d-flex align-center justify-start">
        <v-btn
          variant="tonal"
          size="large"
          :color="selected === 'mitarbeiter' ? 'primary' : 'blue-grey'"
          @click="(selected = 'mitarbeiter'), clearStandort(), clearGruppe()"
        >
          Personal
        </v-btn>
        <v-divider class="flex-grow-1 ml-2"></v-divider>
      </v-col>
    </v-row>

    <v-row justify="center" class="mt-4">
      <v-col cols="6">
        <v-card
          v-if="selected === 'standort'"
          class="pa-4 text-blue-grey-darken-3 ms-n2 me-n8"
        >
          <v-card-title class="text-h6">
            Abrechnung für einen Standort
          </v-card-title>
          <v-card-text>
            Standort, für welchen die Abrechnung erstellt werden soll,
            auswählen.
            <v-menu>
              <template #activator="{ props }">
                <v-text-field
                  :active="true"
                  base-color="blue-grey"
                  color="primary"
                  variant="outlined"
                  Placeholder="Standort auswählen"
                  class="mt-10 text-blue-grey-darken-3"
                  v-bind="props"
                  v-model="selectedLocationName"
                  label="Standort"
                  clearable
                  readonly
                  append-inner-icon="mdi-chevron-down"
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
            <v-menu
              v-model="dateMenu1"
              location="center"
              transition="scale-transition"
            >
              <template v-slot:activator="{ props }">
                <v-text-field
                  :active="true"
                  base-color="blue-grey"
                  color="primary"
                  variant="outlined"
                  Placeholder="Monat auswählen"
                  class="mt-3 mb-n2"
                  label="Monat"
                  v-model="selectedMonthFormatted"
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
          <v-card-actions class="justify-end me-2">
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

        <v-card
          v-if="selected === 'gruppe'"
          class="pa-4 text-blue-grey-darken-3 ms-n2 me-n8"
        >
          <v-card-title class="text-h6">
            Abrechnung für eine Gruppe
          </v-card-title>
          <v-card-text>
            Gruppe, für welche die Abrechnung erstellt werden soll, auswählen.
            <v-menu offset-y>
              <template #activator="{ props }">
                <v-text-field
                  :active="true"
                  base-color="blue-grey"
                  color="primary"
                  variant="outlined"
                  Placeholder="Gruppe auswählen"
                  class="mt-10"
                  v-bind="props"
                  v-model="selectedGroupName"
                  label="Gruppe auswählen"
                  readonly
                  clearable
                  append-inner-icon="mdi-chevron-down"
                ></v-text-field>
              </template>
              <v-list class="w-50">
                <v-list-item v-for="location in locations" :key="location.id">
                  <v-list-item-title class="cursor-pointer">{{
                    location?.location_name
                  }}</v-list-item-title>

                  <template v-slot:append>
                    <v-icon icon="mdi-menu-right" size="x-small"></v-icon>
                  </template>

                  <v-menu
                    offset-y
                    activator="parent"
                    open-on-click
                    close-on-content-click
                    location="end"
                  >
                    <v-list>
                      <v-list-item
                        v-for="group in getGroupsByLocation(location.id)"
                        :key="group.id"
                        @click="selectGroup(group)"
                      >
                        <v-list-item-title>{{
                          group.group_name
                        }}</v-list-item-title>
                      </v-list-item>
                      <v-list-item
                        v-if="getGroupsByLocation(location.id).length === 0"
                      >
                        <v-list-item-title class="text-blue-grey"
                          >Besitzt keine Gruppen!</v-list-item-title
                        >
                      </v-list-item>
                    </v-list>
                  </v-menu>
                </v-list-item>
              </v-list>
            </v-menu>
            <v-menu
              v-model="dateMenu2"
              location="center"
              transition="scale-transition"
            >
              <template v-slot:activator="{ props }">
                <v-text-field
                  :active="true"
                  base-color="blue-grey"
                  color="primary"
                  variant="outlined"
                  Placeholder="Monat auswählen"
                  class="mt-3 mb-n2"
                  v-model="selectedMonthFormatted"
                  label="Monat"
                  readonly
                  v-bind="props"
                  append-inner-icon="mdi-chevron-down"
                ></v-text-field>
              </template>

              <v-list>
                <v-list-item
                  v-for="month in lastSixMonths"
                  :key="month.value"
                  @click="selectMonth(month)"
                >
                  <v-list-item-title class="text-blue-grey-darken-3">{{
                    month.label
                  }}</v-list-item-title>
                </v-list-item>
              </v-list>
            </v-menu>
          </v-card-text>
          <v-card-actions class="justify-end me-2">
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

        <v-card
          v-if="selected === 'mitarbeiter'"
          class="pa-4 text-blue-grey-darken-3 ms-n2 me-n8"
        >
          <v-card-title class="text-h6"> Abrechnung für Personal </v-card-title>
          <v-card-text>
            Person, für welche eine Abrechnung erstellt werden soll, auswählen.
            <v-text-field
              :active="true"
              base-color="blue-grey"
              color="primary"
              variant="outlined"
              Placeholder="Person auswählen"
              class="mt-10"
              v-model="selectedPersonName"
              label="Person"
              readonly
              append-inner-icon="mdi-chevron-down"
              @click="(personDialog = true), (isSearchVisible = false)"
            ></v-text-field>
            <v-menu
              v-model="dateMenu3"
              location="center"
              transition="scale-transition"
            >
              <template v-slot:activator="{ props }">
                <v-text-field
                  :active="true"
                  base-color="blue-grey"
                  color="primary"
                  variant="outlined"
                  Placeholder="Monat auswählen"
                  class="mt-3 mb-n2"
                  label="Monat"
                  v-model="selectedMonthFormatted"
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
          <v-card-actions class="justify-end me-2">
            <v-btn
              color="primary"
              variant="elevated"
              :disabled="
                !selectedPersonId ||
                selectedPersonId.length < 1 ||
                !selectedMonth
              "
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
    <v-card class="text-blue-grey-darken-3 px-5">
      <v-spacer></v-spacer>

      <div class="d-flex h-100 align-center justify-space-between pe-6 mt-5">
        <h2 class="text-blue-grey-darken-3 ml-6">Personal</h2>
        <div class="w-50">
          <v-slide-x-reverse-transition>
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
          </v-slide-x-reverse-transition>
        </div>
        <v-btn
          class="bg-blue-grey"
          size="35"
          icon="mdi-magnify"
          @click="toggleSearchField"
        ></v-btn>
      </div>
      <v-card-text>
        <v-data-table
          class="text-blue-grey"
          :headers="headers"
          :items="items"
          :search="search"
          item-value="id"
          v-model="selectedPersonId"
          show-select
          select-strategy="single"
          dense
          hover
          @update:model-value="check"
        >
        </v-data-table>
      </v-card-text>
      <v-card-actions class="justify-end mt-n5 mb-2 me-3">
        <v-btn
          @click="
            (personDialog = false), (selectedPersonId = null), (checked = false)
          "
          color="blue-grey"
          variant="text"
          >Abbrechen</v-btn
        >
        <v-btn
          :disabled="!checked"
          color="primary"
          variant="elevated"
          @click="personDialog = false"
        >
          Übernehmen
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import axios from "axios";
import { useFeedbackStore } from "@/stores/feedback";
const feedbackStore = useFeedbackStore();
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
const checked = ref(false);

const headers = [
  { titel: "Tätigkeit", key: "tätigkeit", nowrap: true },
  { title: "Vorname", key: "first_name", nowrap: true },
  { title: "Nachname", key: "last_name", nowrap: true },
  { title: "Standort", key: "location_name", nowrap: true },
  { title: "Gruppe", key: "group_name", nowrap: true },
];

const check = () => {
  checked.value = selectedPersonId.value.length !== 0;
};

const clearStandort = () => {
  selectedLocationName.value = null;
  selectedDates1.value = [];
  console.log(selectedLocationName.value);
};
const clearGruppe = () => {
  selectedGroupName.value = null;
  selectedDates2.value = [];
};
const clearPerson = () => {
  selectedPersonName.value = null;
  selectedDates3.value = [];
};

const toggleSearchField = () => {
  if (isSearchVisible.value) {
    search.value = "";
  }
  isSearchVisible.value = !isSearchVisible.value;
};

const lastSixMonths = computed(() => {
  const months = [];
  const monthNames = [
    "Januar",
    "Februar",
    "März",
    "April",
    "Mai",
    "Juni",
    "Juli",
    "August",
    "September",
    "Oktober",
    "November",
    "Dezember",
  ];

  const today = new Date();
  for (let i = 1; i <= 6; i++) {
    const date = new Date(today.getFullYear(), today.getMonth() - i, 1);
    const monthLabel = `${monthNames[date.getMonth()]} ${date.getFullYear()}`;
    const monthValue = `${date.getFullYear()}-${String(
      date.getMonth() + 1
    ).padStart(2, "0")}`;

    months.push({ label: monthLabel, value: monthValue });
  }
  return months;
});

const selectedMonthFormatted = computed(() => {
  return selectedMonth.value
    ? lastSixMonths.value.find((m) => m.value === selectedMonth.value)?.label
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
      tätikeit: "Gruppenmitglied",
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
          : user.user_group,
    })),
  ];
};

watch(selectedPersonId, (newId) => {
  if (newId) {
    const person = items.value.find((item) => item.id === newId[0]);
    selectedPersonName.value = person
      ? `${person.first_name} ${person.last_name}`
      : null;
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
    .get(import.meta.env.VITE_API + "/api/invoices", {
      params: {
        [idName]: id,
        "date-start": startDate,
        "date-end": endDate,
      },
      withCredentials: true,
      responseType: "blob",
    })
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
      feedbackStore.setFeedback("success", "snackbar", "", "Die Abrechnung für " + selectedMonthFormatted.value + " wurde erfolgreich erstellt.");
    })
    .catch((err) => {
      console.error(err.response.data.description);
      feedbackStore.setFeedback("error", "snackbar", err.response?.data?.title, err.response?.data?.description);
    });
};

onMounted(() => {
  axios
    .get(import.meta.env.VITE_API + "/api/locations", { withCredentials: true })
    .then((response) => {
      locations.value = response.data;
    })
    .catch((err) => {
      console.error("Error fetching data", err);
      feedbackStore.setFeedback("error", "snackbar", err.response?.data?.title, err.response?.data?.description);
    });
  axios
    .get(import.meta.env.VITE_API + "/api/groups", {
      withCredentials: true,
    })
    .then((response) => {
      groups.value = response.data;
    })
    .catch((err) => {
      console.error("Error fetching data", err);
      feedbackStore.setFeedback("error", "snackbar", err.response?.data?.title, err.response?.data?.description);
    });
  axios
    .get(import.meta.env.VITE_API + "/api/employees", { withCredentials: true })
    .then((response) => {
      employees.value = response.data;
      setItems();
    })
    .catch((err) => {
      console.error("Error fetching data", err);
      feedbackStore.setFeedback("error", "snackbar", err.response?.data?.title, err.response?.data?.description);
    });
  axios
    .get(import.meta.env.VITE_API + "/api/users", { withCredentials: true })
    .then((response) => {
      users.value = response.data;
      setItems();
    })
    .catch((err) => {
      console.error("Error fetching data", err);
      feedbackStore.setFeedback("error", "snackbar", err.response?.data?.title, err.response?.data?.description);
    });
});
</script>
