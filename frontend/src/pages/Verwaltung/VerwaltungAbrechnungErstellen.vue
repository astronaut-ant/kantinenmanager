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
            <v-text-field
              :active="true"
              base-color="blue-grey"
              color="primary"
              variant="outlined"
              class="mt-5"
              Placeholder="Zeitraum auswählen"
              v-model="formattedDateRange1"
              label="Zeitraum"
              readonly
              append-inner-icon="mdi-chevron-down"
              @click="showDialog1 = true"
            ></v-text-field>
          </v-card-text>
          <v-card-actions class="justify-end me-2">
            <v-btn
              color="primary"
              variant="elevated"
              :disabled="!selectedLocationName || selectedDates1.length === 0"
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
            <v-text-field
              :active="true"
              base-color="blue-grey"
              color="primary"
              variant="outlined"
              class="mt-5"
              placeholder="Zeitraum auswählen"
              v-model="formattedDateRange2"
              label="Zeitraum"
              readonly
              append-inner-icon="mdi-chevron-down"
              @click="showDialog2 = true"
            ></v-text-field>
          </v-card-text>
          <v-card-actions class="justify-end me-2">
            <v-btn
              color="primary"
              variant="elevated"
              :disabled="!selectedGroupName || selectedDates2.length === 0"
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
            <v-text-field
              :active="true"
              base-color="blue-grey"
              color="primary"
              variant="outlined"
              class="mt-5"
              Placeholder="Zeitraum auswählen"
              v-model="formattedDateRange3"
              label="Zeitraum"
              readonly
              append-inner-icon="mdi-chevron-down"
              @click="showDialog3 = true"
            ></v-text-field>
          </v-card-text>
          <v-card-actions class="justify-end me-2">
            <v-btn
              color="primary"
              variant="elevated"
              :disabled="!selectedPersonName || selectedDates3.length === 0"
              @click="generateInvoice()"
            >
              Erstellen
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>

  <v-dialog v-model="showDialog1" max-width="400">
    <v-card class="text-blue-grey-darken-3">
      <v-card-title class="text-h5 mt-2 ms-7 mb-n2">
        Zeitraum auswählen
      </v-card-title>

      <v-card-text>
        <v-date-picker
          color="primary"
          v-model="selectedDates1"
          multiple="range"
          :min="minDate"
          :max="maxDate"
          hide-header
        />
      </v-card-text>
      <span class="text-center text-blue-grey mt-n6 mb-8 font-weight-bold">
        {{ formattedDateRange1 }}
      </span>

      <div class="px-12">
        <v-divider></v-divider>
      </div>

      <v-card-actions class="justify-end me-7">
        <v-btn
          color="blue-grey"
          variant="text"
          @click="(showDialog1 = false), (selectedDates1 = [])"
        >
          Abbrechen
        </v-btn>
        <v-btn
          :disabled="selectedDates1.length === 0"
          color="primary"
          variant="elevated"
          @click="showDialog1 = false"
        >
          Übernehmen
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

  <v-dialog v-model="showDialog2" max-width="400">
    <v-card class="text-blue-grey-darken-3">
      <v-card-title class="text-h5 mt-2 ms-7 mb-n2">
        Zeitraum auswählen
      </v-card-title>

      <v-card-text>
        <v-date-picker
          color="primary"
          v-model="selectedDates2"
          multiple="range"
          :min="minDate"
          :max="maxDate"
          hide-header
        />
      </v-card-text>
      <span class="text-center text-blue-grey mt-n6 mb-8 font-weight-bold">
        {{ formattedDateRange2 }}
      </span>

      <div class="px-12">
        <v-divider></v-divider>
      </div>

      <v-card-actions class="justify-end me-7">
        <v-btn
          color="blue-grey"
          variant="text"
          @click="(showDialog2 = false), (selectedDates2 = [])"
        >
          Abbrechen
        </v-btn>
        <v-btn
          :disabled="selectedDates2.length === 0"
          color="primary"
          variant="elevated"
          @click="showDialog2 = false"
        >
          Übernehmen
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

  <v-dialog v-model="showDialog3" max-width="400">
    <v-card class="text-blue-grey-darken-3">
      <v-card-title class="text-h5 mt-2 ms-7 mb-n2">
        Zeitraum auswählen
      </v-card-title>

      <v-card-text>
        <v-date-picker
          color="primary"
          v-model="selectedDates3"
          multiple="range"
          :min="minDate"
          :max="maxDate"
          hide-header
        />
      </v-card-text>
      <span class="text-center text-blue-grey mt-n6 mb-8 font-weight-bold">
        {{ formattedDateRange2 }}
      </span>

      <div class="px-12">
        <v-divider></v-divider>
      </div>

      <v-card-actions class="justify-end me-7">
        <v-btn
          color="blue-grey"
          variant="text"
          @click="(showDialog3 = false), (selectedDates3 = [])"
        >
          Abbrechen
        </v-btn>
        <v-btn
          :disabled="selectedDates3.length === 0"
          color="primary"
          variant="elevated"
          @click="showDialog3 = false"
        >
          Übernehmen
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

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
const selected = ref("");
const selectedDates1 = ref([]);
const selectedDates2 = ref([]);
const selectedDates3 = ref([]);
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
const showDialog1 = ref(false);
const showDialog2 = ref(false);
const showDialog3 = ref(false);
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

const today = new Date();
const sixMonthsAgo = new Date();
sixMonthsAgo.setMonth(today.getMonth() - 6);

const minDate = computed(() => sixMonthsAgo.toISOString().split("T")[0]);
const maxDate = computed(() => today.toISOString().split("T")[0]);

const formattedDateRange1 = computed(() => {
  if (selectedDates1.value.length === 0) return "";
  return `${selectedDates1.value[0].toLocaleDateString(
    "de-DE"
  )} - ${selectedDates1.value[
    selectedDates1.value.length - 1
  ].toLocaleDateString("de-DE")}`;
});
const formattedDateRange2 = computed(() => {
  if (selectedDates2.value.length === 0) return "";
  return `${selectedDates2.value[0].toLocaleDateString(
    "de-DE"
  )} - ${selectedDates2.value[
    selectedDates2.value.length - 1
  ].toLocaleDateString("de-DE")}`;
});
const formattedDateRange3 = computed(() => {
  if (selectedDates3.value.length === 0) return "";
  return `${selectedDates3.value[0].toLocaleDateString(
    "de-DE"
  )} - ${selectedDates3.value[
    selectedDates3.value.length - 1
  ].toLocaleDateString("de-DE")}`;
});

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
  let selectedDatesRef = null;
  let idName = null;

  if (selected.value === "standort") {
    id = selectedLocation.value?.id;
    idName = "location-id";
    selectedDatesRef = selectedDates1?.value;
  } else if (selected.value === "gruppe") {
    id = selectedGroup.value?.id;
    idName = "group-id";
    selectedDatesRef = selectedDates2?.value;
  } else if (selected.value === "mitarbeiter") {
    id = selectedPersonId?.value[0];
    idName = "person-id";
    selectedDatesRef = selectedDates3?.value;
  }

  if (!id || !idName || !selectedDatesRef || selectedDatesRef.length < 1) {
    console.log("Fehlende Eingaben!");
    return;
  }

  const startDate = selectedDatesRef[0].toLocaleDateString("fr-CA");
  const endDate =
    selectedDatesRef[selectedDatesRef.length - 1].toLocaleDateString("fr-CA");

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
    })
    .catch((err) => {
      console.log(err.response.data.description);
    });
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
