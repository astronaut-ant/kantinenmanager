<template>
  <NavbarGruppenleitung :breadcrumbs = '[{"title": "Meine Gruppen"}]'/>
  <v-container max-width="800">
    <div>
      <v-toolbar color="white" flat dark >
        <div class="d-flex justify-center">
          <p class="text-h5 font-weight-black">Meine Gruppe</p>
        </div>
      </v-toolbar>
    </div>
    <div>
      <v-data-table-virtual
        :headers="headers"
        :items="mygroup"
        :loading="loading"
        :hover="true"
        item-value="employee_number"
        density="comfortable"
      >
      </v-data-table-virtual>
    </div>
    <div v-for="(group, index) in othergroups" :key="index" class="mt-5">
      <v-toolbar color="white" flat dark>
        <p class="text-h5 font-weight-black">Gruppe {{ group[0].group.group_name }}</p>
      </v-toolbar>
      <v-data-table-virtual
        :headers="headers"
        :items="group"
        :loading="loading"
        :hover="true"
        item-value="employee_number"
        density="comfortable"
      ></v-data-table-virtual>
    </div>
  </v-container>
</template>

<script setup>
import { useAppStore } from "@/stores/app";
import axios from "axios";
import { ref } from "vue";
import { useFeedbackStore } from "@/stores/feedback";
const feedbackStore = useFeedbackStore();
const appStore = useAppStore();
const id = appStore.userData.id;


const employees = ref([]);
const mygroup = ref([]);
const othergroups = ref([]);
const loading = ref(false);


const headers = [
  { title: "Nummer", key: "employee_number", nowrap: true},
  { title: "Nachname", key: "last_name", nowrap: true },
  { title: "Vorname", key: "first_name", nowrap: true }
];

  const fetchDataWithId = () => {
    loading.value = true;

    axios
      .get(import.meta.env.VITE_API + "/api/employees", { withCredentials: true })
      .then((response) => {
        employees.value = response.data;

        const groupedEmployees = employees.value.reduce((acc, employee) => {
          const leaderId = employee.group?.user_id_group_leader || "Unassigned";

          if (!acc[leaderId]) {
            acc[leaderId] = [];
          }

          acc[leaderId].push(employee);
          return acc;
        }, {});

        mygroup.value = groupedEmployees[id];
        othergroups.value = Object.keys(groupedEmployees)
          .filter((key) => key !== id)
          .map((key) => groupedEmployees[key]);

        loading.value = false;
        //console.log("Grouped Employees:", groupedEmployees);
      })
      .catch((err) => {
        console.error("Error fetching data", err);
        feedbackStore.setFeedback("error", "snackbar", err.response?.data?.title, err.response?.data?.description);
        loading.value = false;
      });
  };

  onMounted(() => {
    fetchDataWithId();
  });

</script>
