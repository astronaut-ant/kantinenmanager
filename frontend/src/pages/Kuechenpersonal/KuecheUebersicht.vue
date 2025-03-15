<template>
  <NavbarKueche :breadcrumbs="[{ title: 'Heutige Bestellungen' }]" />
  <h1 class="text-center text-blue-grey mt-5">Heutige Bestellungen</h1>
  <v-container class="py-10 d-flex ga-15 justify-space-between w-75">
    <v-card
      elevation="5"
      class="ms-n4 text-center w-100 text-blue-grey custom-card"
    >
      <v-card-title>Blaues Hauptgericht</v-card-title>
      <v-card-text>
        <div class="d-flex h-100 align-center justify-center ga-2">
          <v-icon color="primary" size="36">mdi-circle</v-icon>
          <h3>{{ orderCount.blau }}</h3>
        </div>
      </v-card-text>
    </v-card>

    <v-card elevation="5" class="text-center w-100 text-blue-grey custom-card">
      <v-card-title>Rotes Hauptgericht</v-card-title>
      <v-card-text>
        <div class="d-flex h-100 align-center justify-center ga-2">
          <v-icon color="red" size="36">mdi-circle</v-icon>
          <h3>{{ orderCount.rot }}</h3>
        </div>
      </v-card-text>
    </v-card>
    <v-card
      elevation="5"
      class="text-center w-100 text-blue-grey custom-card me-n4"
    >
      <v-card-title>Salat</v-card-title>
      <v-card-text>
        <div class="d-flex h-100 align-center justify-center ga-2">
          <v-icon color="green" size="36">mdi-leaf</v-icon>
          <h3>{{ orderCount.salad_option }}</h3>
        </div>
      </v-card-text>
    </v-card>
  </v-container>
  <v-data-table-virtual
    class="mx-auto w-75 text-blue-grey-darken-1"
    :hover="true"
    :fixed-header="true"
    :height="tableHeight"
    :items="tableData"
    item-key="id"
    :headers="headers"
    :sort-by="sortBy"
  >
    <template v-slot:item="{ item }">
      <tr class="hover-row">
        <td>
          {{ item.full_name }}
        </td>
        <td>
          {{ item.group_name }}
        </td>
        <td>
          <v-icon
            :color="
              item.main_dish === 'rot'
                ? 'red'
                : item.main_dish === 'blau'
                ? 'primary'
                : 'grey'
            "
            size="24"
          >
            mdi-circle
          </v-icon>
        </td>
        <td>
          <v-icon :color="item.salad_selected ? 'green' : 'grey'" size="24">
            mdi-circle
          </v-icon>
        </td>
        <td>
          <v-btn
            :icon="item.handed_out ? 'mdi-check' : 'mdi-close'"
            density="compact"
            @click="openConfirmDialog(item)"
          ></v-btn>
        </td>
      </tr>
    </template>
  </v-data-table-virtual>

  <v-dialog v-model="dialog" max-width="400px" persistent>
    <v-card>
      <v-card-title class="headline">Bestätigung</v-card-title>
      <v-card-text>
        Möchten Sie den Status Ausgabe der Bestellung wirklich ändern?
      </v-card-text>
      <v-card-actions>
        <v-btn color="red darken-1" text @click="closeConfirmDialog"
          >Abbrechen</v-btn
        >
        <v-btn color="green darken-1" text @click="confirmChange"
          >Bestätigen</v-btn
        >
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import axios from "axios";
import { useFeedbackStore } from "@/stores/feedback";
const feedbackStore = useFeedbackStore();


const orders = ref([]);
const employees = ref([]);
const locations = ref([]);
const allLocationLeadersIds = ref([]);
const groupleaders = ref([]);
const users = ref([]);
const tableData = ref([]);
const dialog = ref(false);
const itemToConfirm = ref(null);
const orderCount = ref({
  blau: 0,
  rot: 0,
  salad_option: 0,
});

const sortBy = [{ key: "full_name", order: "asc" }];

const tableHeight = computed(() => {
  const headerHeight = 80; // Höhe der Navbar
  return window.innerHeight - headerHeight - 100 + "px";
});

const headers = ref([
  {
    title: "Name",
    value: "full_name",
    key: "full_name",
    sortable: true,
  },
  { title: "Bereich", value: "group_name", sortable: "true" },
  { title: "Hauptgericht", value: "main_dish", sortable: "true" },
  {
    title: "Salat",
    value: "salad_selected",
    sortable: "true",
  },
  {
    title: "Ausgehändigt",
    value: "handed_out",
    sortable: "true",
  },
]);

// Daten laden und verbinden
const getCount = () => {
  axios
    .get(import.meta.env.VITE_API + "/api/daily-orders/counted", {
      withCredentials: true,
    })
    .then((response) => {
      orderCount.value = response.data[0] || {
        blau: 0,
        rot: 0,
        salad_option: 0,
      };
      console.log("Count: ", orderCount.value);
    })
    .catch((err) => {
      console.error(err);
      feedbackStore.setFeedback("error", "snackbar", err.response?.data?.title, err.response?.data?.description);
    });
};

const fillTable = () => {
  getOrders();
};

const getOrders = () => {
  axios
    .get(import.meta.env.VITE_API + "/api/daily-orders", {
      withCredentials: true,
    })
    .then((response) => {
      orders.value = response.data;
      console.log("Daily Orders: ", orders.value);
      getEmployees();
    })
    .catch((err) => {
      console.error(err);
      feedbackStore.setFeedback("error", "snackbar", err.response?.data?.title, err.response?.data?.description);
    });
};

const getEmployees = () => {
  axios
    .get(import.meta.env.VITE_API + "/api/employees", {
      withCredentials: true,
    })
    .then((response) => {
      employees.value = response.data;
      console.log("All Emplyees: ", employees.value);
      getUsers();
    })
    .catch((err) => {
      console.error(err);
      feedbackStore.setFeedback("error", "snackbar", err.response?.data?.title, err.response?.data?.description);
    });
};

const getUsers = () => {
  axios
    .get(import.meta.env.VITE_API + "/api/users", { withCredentials: true })
    .then((response) => {
      users.value = response.data;
      console.log("All Users: ", users.value);
      getLocations();
    })
    .catch((err) => {
      console.error(err);
      feedbackStore.setFeedback("error", "snackbar", err.response?.data?.title, err.response?.data?.description);
    });
};
const getLocations = () => {
  axios
    .get(import.meta.env.VITE_API + "/api/locations", { withCredentials: true })
    .then((response) => {
      locations.value = response.data;
      locations.value.forEach((location) =>
        allLocationLeadersIds.value.push(location.location_leader.id)
      );
      console.log("All Locations: ", locations.value);
      console.log("allLocationLeadsIds: ", allLocationLeadersIds.value);
      getGroupLeaders();
    })
    .catch((err) => {
      console.error(err);
      feedbackStore.setFeedback("error", "snackbar", err.response?.data?.title, err.response?.data?.description);
    });
};
const getGroupLeaders = () => {
  axios
    .get(import.meta.env.VITE_API + "/api/users/group-leaders", {
      withCredentials: true,
    })
    .then((response) => {
      groupleaders.value = response.data;
      groupleaders.value.forEach((groupleader) => {
        if (groupleader.own_group === null) {
          groupleader.own_group = { group_name: "Ohne Gruppe" };
        }
      });
      console.log("All GroupLeaders: ", groupleaders.value);
      updateTableData();
    })
    .catch((err) => {
      console.error(err);
      feedbackStore.setFeedback("error", "snackbar", err.response?.data?.title, err.response?.data?.description);
    });
};

// Daten zusammenführen

const updateTableData = () => {
  if (orders.value.length === 0) return;
  const persons = joinEmployeesAndUsers();
  console.log(persons);
  tableData.value = orders.value.map((order) => {
    const person = persons.find((person) => person.id === order.person_id);
    let role;
    if (person.employee_number !== undefined) {
      role = `Mitarbeiter (${person.group.group_name})`;
    } else if (
      person.user_group === "standortleitung" ||
      person.user_group === "kuechenpersonal"
    ) {
      if (allLocationLeadersIds.value.includes(person.id)) {
        role = `${formatted(person.user_group)} (${formatted(
          locations.value.find((location) => location.id === person.location_id)
            .location_name
        )})`;
      } else {
        role = `${formatted(person.user_group)} (Ohne Standort)`;
      }
    } else if (person.user_group === "gruppenleitung") {
      console.log(person.id);
      role = `${formatted(person.user_group)} (${formatted(
        groupleaders.value.find((groupleader) => groupleader.id == person.id)
          .own_group.group_name
      )})`;
    } else {
      role = formatted(person.user_group);
    }

    return {
      id: order.id,
      full_name: `${person.first_name} ${person.last_name}`,
      group_name: role,
      main_dish: order.main_dish || "Keine Angabe",
      main_dish_selected: order.main_dish === "rot",
      salad_selected: order.salad_option,
      handed_out: order.handed_out,
    };
  });
};
const joinEmployeesAndUsers = () => {
  return employees.value.concat(users.value);
};
const formatted = (role) => {
  let capitalized = role.charAt(0).toUpperCase() + role.slice(1);
  return capitalized.replace("ue", "ü");
};

const openConfirmDialog = (item) => {
  itemToConfirm.value = item;
  dialog.value = true;
};
const confirmChange = () => {
  axios
    .put(
      import.meta.env.VITE_API + `/api/daily-orders/${itemToConfirm.value.id}`,
      { handed_out: !itemToConfirm.value.handed_out },
      { withCredentials: true }
    )
    .then(() => {
      itemToConfirm.value.handed_out = !itemToConfirm.value.handed_out;
      closeConfirmDialog();
    })
    .catch((err) => {
      console.error(err);
      feedbackStore.setFeedback("error", "snackbar", err.response?.data?.title, err.response?.data?.description);
    });
};
const closeConfirmDialog = () => {
  itemToConfirm.value = null;
  dialog.value = false;
};
getCount();
fillTable();
</script>
<style scoped>
.hover-row:hover {
  background-color: #eceff1; /* Choose your desired color */
  color: #37474f;
}
.custom-card {
  border: 1px solid #607d8b; /* Set your desired border color */
}
</style>
