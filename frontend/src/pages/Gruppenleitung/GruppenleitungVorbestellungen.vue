<template>
  <NavbarGruppenleitung />
  <h1 class="text-center mt-5 mb-5">Vorbestellungen</h1>
  <div class="ps-10 pe-10">
    <FullCalendar :options="calendarOptions" />
    <CalendarDialog :showDialog="showDialog" @close="this.showDialog = false" />
  </div>
</template>

<script>
import FullCalendar from "@fullcalendar/vue3";
import dayGridPlugin from "@fullcalendar/daygrid";
import interactionPlugin from "@fullcalendar/interaction";
import CalendarDialog from "@/components/CalendarDialog.vue";

export default {
  components: {
    FullCalendar, // make the <FullCalendar> tag available
  },
  data() {
    return {
      showDialog: false,
      calendarOptions: {
        plugins: [dayGridPlugin, interactionPlugin],
        initialView: "dayGridMonth",
        dateClick: this.handleDateClick,
        events: [
          { title: "Gruppe 1", date: "2024-12-07" },
          {
            title: "Gruppe 2 (Vertretung)",
            date: "2024-12-07",
            backgroundColor: "hotpink",
            borderColor: "white",
          },
        ],
      },
    };
  },
  methods: {
    handleDateClick: function (arg) {
      //alert("date click! " + arg.dateStr);
      this.showDialog = true;
      this.calendarOptions.events.push({ title: "Gruppe1", date: arg.dateStr });
    },
  },
};
</script>
