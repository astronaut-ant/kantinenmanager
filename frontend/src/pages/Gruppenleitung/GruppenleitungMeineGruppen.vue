<template>
  <NavbarGruppenleitung />
  <v-container max-width="1000">
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
        <template v-slot:[`item.actions`]="{ item }">
          <v-btn
            icon="mdi-qrcode"
            class="bg-green mr-2"
            @click="getQRCode(item)"
            size="small"
          ></v-btn>
        </template>
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
      >
        <template v-slot:[`item.actions`]="{ item }">
          <v-btn
            icon="mdi-qrcode"
            class="bg-green mr-2"
            @click="getQRCode(item)"
            size="small"
          ></v-btn>
        </template>
      </v-data-table-virtual>
    </div>
  </v-container>
</template>

<script setup>
import axios from "axios";
import { ref } from "vue";

const id = ref("");
const employees = ref([]);
const mygroup = ref([]);
const othergroups = ref([]);
const loading = ref(false);


const headers = [
  { title: "Nummer", key: "employee_number", nowrap: true},
  { title: "Nachname", key: "last_name", nowrap: true },
  { title: "Vorname", key: "first_name", nowrap: true },
  { text: "Actions", value: "actions", sortable: false },
];

  const fetchDataWithId = () => {
    loading.value = true;

    axios
      .get(import.meta.env.VITE_API + "/api/is-logged-in", { withCredentials: true })
      .then((response) => {
        id.value = response.data.id;
        return axios.get(import.meta.env.VITE_API + "/api/employees", { withCredentials: true });
      })
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

        mygroup.value = groupedEmployees[id.value];
        othergroups.value = Object.keys(groupedEmployees)
          .filter((key) => key !== id.value)
          .map((key) => groupedEmployees[key]);

        loading.value = false;
      })
      .catch((err) => {
        console.error("Error fetching data", err);
        loading.value = false;
      });
  };

  const getQRCode = (item) => {
  axios
    .get(`${import.meta.env.VITE_API}/api/persons/create-qr/${item.id}`, {
      responseType: "blob",
      withCredentials: true,
    })
    .then((response) => {
      const blob = new Blob([response.data], { type: response.headers["content-type"] });
      const url = window.URL.createObjectURL(blob);

      const link = document.createElement("a");
      link.href = url;

      const contentDisposition = response.headers["content-disposition"];
      let filename = "download";
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename\*?=(['"]?)(.+?)\1(;|$)/i);
        if (filenameMatch) {
          filename = decodeURIComponent(filenameMatch[2]);
        }
      }

      link.download = filename;
      link.click();
      window.URL.revokeObjectURL(url);
    })
    .catch((err) => {
      console.error("Error getting QR Code", err);
    });
  };

  onMounted(() => {
    fetchDataWithId();
  });

</script>
