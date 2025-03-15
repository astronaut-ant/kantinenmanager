<template>
  <NavbarVerwaltung
    :breadcrumbs="[{ title: 'Abrechnung' }, { title: 'Preise anpassen' }]"
  />

  <v-card class="pa-5 mx-auto mt-15" max-width="900">
    <v-card-title class="text-h4 font-weight-bold ms-2 mb-2 text-primary">
      <v-icon :size="36" class="me-3 ms-n2 mt-n1">mdi-currency-eur</v-icon
      >Essenspreise</v-card-title
    >
    <v-card-text>
      <v-data-table
        :headers="headers"
        :items="formattedMeals"
        dense
        :sort-by="sortBy"
      >
        <template v-slot:[`item.actions`]="{ item }">
          <v-btn
            icon="mdi-lead-pencil"
            class="bg-primary mr-2"
            @click="openEditDialog(item)"
            size="small"
          ></v-btn>
          <v-btn
            icon="mdi-trash-can-outline"
            class="bg-red"
            @click="openDeleteDialog(item)"
            size="small"
          ></v-btn>
        </template>
      </v-data-table>
    </v-card-text>
    <v-card-actions class="d-flex justify-end">
      <v-btn class="bg-primary text-white" @click="openAddDialog()">
        <v-icon left>mdi-plus</v-icon> Neuer Preis
      </v-btn>
    </v-card-actions>
  </v-card>

  <v-dialog v-model="editDialog" persistent max-width="600px">
    <v-card>
      <v-card-text>
        <div class="d-flex ga-3 mb-8 text-primary">
          <div class="d-flex align-center">
            <v-icon class="mt-n1" size="35">mdi-tag-edit-outline</v-icon>
          </div>
          <h2>Essenspreis bearbeiten</h2>
        </div>
        <v-form>
          <v-text-field
            v-model="mainDishEdit"
            class="mt-4"
            :active="true"
            base-color="blue-grey"
            color="primary"
            variant="outlined"
            Placeholder="Hauptgericht Preis (€)"
            label="Hauptgericht (€)"
            type="number"
            :rules="[required]"
          ></v-text-field>
          <v-text-field
            v-model="saladEdit"
            class="mt-4"
            :active="true"
            base-color="blue-grey"
            color="primary"
            variant="outlined"
            Placeholder="Salat Preis (€)"
            label="Salat (€)"
            type="number"
            :rules="[required]"
          ></v-text-field>
          <v-text-field
            v-model="prepaymentEdit"
            class="mt-4"
            :active="true"
            base-color="blue-grey"
            color="primary"
            variant="outlined"
            Placeholder="Vorauszahlung (€)"
            label="Vorauszahlung (€)"
            type="number"
            :rules="[required]"
          ></v-text-field>
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-btn @click="closeEditDialog()" color="blue-grey">Abbrechen</v-btn>
        <v-btn
          @click="saveChanges()"
          color="primary"
          class="me-4"
          variant="elevated"
          :disabled="!mainDishEdit || !saladEdit || !prepaymentEdit"
          >Speichern</v-btn
        >
      </v-card-actions>
    </v-card>
  </v-dialog>

  <v-dialog v-model="deleteDialog" persistent max-width="600px">
    <v-card>
      <v-card-text v-if="deletableMeal">
        <div class="d-flex justify-center text-red mb-4">
          <p class="text-h5 font-weight-black">Essenspreis löschen</p>
        </div>
        <div class="text-medium-emphasis">
          <p>
            Sind Sie sicher, dass Sie den Essenspreis vom
            <strong>{{ deletableMeal?.startDateF }}</strong> bis zum
            <strong>{{ deletableMeal?.endDateF }}</strong> löschen möchten?
          </p>
          <p>
            Nach dem Löschen werden die Daten(Preise und Vorbezahlung) vom
            <strong>vorherigen Essenspreis</strong> verwendet
          </p>
        </div>
      </v-card-text>
      <v-card-actions>
        <v-btn @click="closeDeleteDialog()">Abbrechen</v-btn>
        <v-btn @click="handleDelete()" color="red" variant="elevated" :disabled="!deletableMeal"
          >Löschen</v-btn
        >
      </v-card-actions>
    </v-card>
  </v-dialog>

  <v-dialog v-model="addDialog" persistent max-width="600px">
    <v-card>
      <v-card-title>
        <h2 class="text-primary headline justify-center ms-2 mt-2">
          Neuer Essenspreis
        </h2>
      </v-card-title>
      <v-card-text>
        <v-text-field
          class="mt-4"
          :active="true"
          base-color="blue-grey"
          color="primary"
          variant="outlined"
          Placeholder="Start-Datum auswählen"
          v-model="startDateAddF"
          label="Start-Datum"
          @click="dateMenu = true"
          readonly
        ></v-text-field>
        <v-text-field
          class="mt-4"
          :active="true"
          base-color="blue-grey"
          color="primary"
          variant="outlined"
          Placeholder="Hauptgericht Preis (€)"
          v-model="mainDishAdd"
          label="Hauptgericht"
          type="number"
          :rules="[required]"
        ></v-text-field>
        <v-text-field
          :active="true"
          class="mt-4"
          base-color="blue-grey"
          color="primary"
          variant="outlined"
          Placeholder="Salat Preis (€)"
          v-model="saladAdd"
          label="Salat"
          type="number"
          :rules="[required]"
        ></v-text-field>
        <v-text-field
          class="mt-4"
          :active="true"
          base-color="blue-grey"
          color="primary"
          variant="outlined"
          Placeholder="Vorrauszahlung in €"
          v-model="prepaymentAdd"
          label="Vorrauszahlung"
          type="number"
          :rules="[required]"
        ></v-text-field>
      </v-card-text>
      <v-card-actions>
        <v-btn @click="closeAddDialog()" variant="text" color="blue-grey"
          >Abbrechen</v-btn
        >
        <v-btn
          @click="handleAdd()"
          color="primary"
          variant="elevated"
          class="me-4"
          :disabled="
            !startDateAdd || !mainDishAdd || !saladAdd || !prepaymentAdd
          "
          >Hinzufügen</v-btn
        >
      </v-card-actions>
    </v-card>
  </v-dialog>

  <v-dialog v-model="dateMenu" max-width="400">
    <v-card>
      <v-card-title> Start Datum auswählen </v-card-title>
      <v-card-text>
        <v-date-picker
          v-model="selectedDate"
          @update:modelValue="confirmDate()"
        ></v-date-picker>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script setup>
import axios from "axios";
const meals = ref([]);
const editDialog = ref(false);
const mainDishEdit = ref(null);
const saladEdit = ref(null);
const prepaymentEdit = ref(null);
const startDateEdit = ref(null);
const deleteDialog = ref(false);
const deletableMeal = ref(null);
const addDialog = ref(false);
const startDateAdd = ref(null);
const startDateAddF = ref(null);
const mainDishAdd = ref(null);
const saladAdd = ref(null);
const prepaymentAdd = ref(null);
const dateMenu = ref(false);
const selectedDate = ref(null);

const headers = [
  { title: "Startdatum", key: "startDateF", nowrap: true },
  { title: "Enddatum", key: "endDateF", nowrap: true },
  { title: "Hauptgericht (€)", key: "mainDishF", nowrap: true },
  { title: "Salat (€)", key: "saladF", nowrap: true },
  { title: "Vorauszahlung (€)", key: "prepaymentF", nowrap: true },
  { title: "", key: "actions", sortable: false, nowrap: true },
];

const sortBy = [{ key: "startDatum", order: "asc" }];

const openEditDialog = (meal) => {
  console.log(meal);
  mainDishEdit.value = meal.mainDish;
  saladEdit.value = meal.salad;
  prepaymentEdit.value = meal.prepayment;
  startDateEdit.value = meal.startDate;
  editDialog.value = true;
};

const closeEditDialog = () => {
  mainDishEdit.value = null;
  saladEdit.value = null;
  prepaymentEdit.value = null;
  startDateEdit.value = null;
  editDialog.value = false;
};

const saveChanges = () => {
  axios
    .put(
      import.meta.env.VITE_API + `/api/dish_prices/${startDateEdit.value}`,
      {
        date: startDateEdit.value,
        main_dish_price: mainDishEdit.value,
        salad_price: saladEdit.value,
        prepayment: prepaymentEdit.value,
      },
      { withCredentials: true }
    )
    .then(() => {
      fetchMeals();
      closeEditDialog();
    })
    .catch((err) => console.log(err));
};

const formattedMeals = computed(() => {
  return meals.value.map((meal, index, arr) => {
    const nextMeal = arr[index + 1];
    const endDate = nextMeal ? getPreviousDay(nextMeal.date) : null;

    return {
      startDateF: formatDate(meal.date),
      endDateF: endDate ? formatDate(endDate) : "Offen",
      mainDishF: meal.main_dish_price.toFixed(2) + " €",
      saladF: meal.salad_price.toFixed(2) + " €",
      prepaymentF: meal.prepayment.toFixed(2) + " €",
      startDate: meal.date,
      mainDish: meal.main_dish_price,
      salad: meal.salad_price,
      prepayment: meal.prepayment,
    };
  });
});

const openDeleteDialog = (meal) => {
  deletableMeal.value = meal;
  console.log(meal);
  console.log(deletableMeal.value);
  deleteDialog.value = true;
};

const closeDeleteDialog = () => {
  deletableMeal.value = null;
  deleteDialog.value = false;
};

const handleDelete = () => {
  axios
    .delete(
      import.meta.env.VITE_API +
        `/api/dish_prices/${deletableMeal.value?.startDate}`,
      { withCredentials: true }
    )
    .then(() => {
      fetchMeals();
      closeDeleteDialog();
    })
    .catch((err) => console.log(err));
};

const openAddDialog = () => {
  addDialog.value = true;
};

const closeAddDialog = () => {
  startDateAdd.value = null;
  mainDishAdd.value = null;
  prepaymentAdd.value = null;
  saladAdd.value = null;
  addDialog.value = false;
};

const confirmDate = () => {
  const dateObj = new Date(selectedDate.value);

  const year = dateObj.getFullYear();
  const month = String(dateObj.getMonth() + 1).padStart(2, "0"); // Monate sind 0-basiert
  const day = String(dateObj.getDate()).padStart(2, "0");

  startDateAddF.value = `${day}.${month}.${year}`;
  startDateAdd.value = `${year}-${month}-${day}`;
};

const handleAdd = () => {
  axios
    .post(
      import.meta.env.VITE_API + "/api/dish_prices",
      {
        date: startDateAdd.value,
        main_dish_price: mainDishAdd.value,
        prepayment: prepaymentAdd.value,
        salad_price: saladAdd.value,
      },
      { withCredentials: true }
    )
    .then((response) => {
      fetchMeals();
      closeAddDialog();
    })
    .catch((err) => console.log("Fehler beim Laden der Essenspreise:", err));
};

const fetchMeals = () => {
  axios
    .get(import.meta.env.VITE_API + "/api/dish_prices", {
      withCredentials: true,
    })
    .then((response) => {
      console.log(response.data);
      meals.value = response.data.sort((a, b) => {
        const dateA = a.date.split("-").map(Number);
        const dateB = b.date.split("-").map(Number);

        return (
          dateA[0] - dateB[0] || dateA[1] - dateB[1] || dateA[2] - dateB[2]
        );
      });
      console.log(meals.value);
    })
    .catch((err) => console.log("Fehler beim Laden der Essenspreise:", err));
};

onMounted(() => {
  fetchMeals();
});

const formatDate = (date) => {
  if (!date) return "";

  const [year, month, day] = date.split("-");
  return `${day}.${month}.${year}`;
};

const getPreviousDay = (date) => {
  const d = new Date(date);
  d.setDate(d.getDate() - 1);
  return d.toISOString().split("T")[0];
};

const required = (v) => {
  return !!v || "Eingabe erforderlich";
};
</script>
