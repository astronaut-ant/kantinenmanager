<template>
  <NavbarGruppenleitung />
  <h1 class="text-center mt-5 mb-5">Vorbestellungen</h1>
  <div class="ps-10 pe-10">
    <FullCalendar :options="calendarOptions" />
    <CalendarDialog
      v-if="showDialog"
      :showDialog="showDialog"
      :date="clickedDate"
      @close="this.showDialog = false"
      @save="addEvent"
    />
    <Bestellformular
      v-if="showBestellformular"
      :date="clickedDate"
      :showBestellformular="showBestellformular"
      @close="showBestellformular = false"
    />
  </div>
</template>

<script>
import FullCalendar from "@fullcalendar/vue3";
import dayGridPlugin from "@fullcalendar/daygrid";
import interactionPlugin from "@fullcalendar/interaction";
import CalendarDialog from "@/components/CalendarDialog.vue";
import Bestellformular from "@/components/Bestellformular.vue";

export default {
  components: {
    FullCalendar, // make the <FullCalendar> tag available
  },
  data() {
    return {
      showDialog: false,
      showBestellformular: false,
      clickedDate: "",
      calendarOptions: {
        plugins: [dayGridPlugin, interactionPlugin],
        initialView: "dayGridMonth",
        dateClick: this.handleDateClick,
        events: [],
      },
    };
  },
  methods: {
    handleDateClick: function (arg) {
      //alert("date click! " + arg.dateStr);
      this.showDialog = true;
      this.clickedDate = arg.dateStr;
    },
    addEvent: function (selectedGroup) {
      const isHomeGroup = selectedGroup === "Gruppe 1";
      this.calendarOptions.events.push({
        title: selectedGroup,
        date: this.clickedDate,
        backgroundColor: isHomeGroup ? "#1867C0" : "#F44336",
        borderColor: isHomeGroup ? "#1867C0" : "#F44336",
      });
      setTimeout(() => {
        this.showBestellformular = true;
      }, "250");
    },
  },
};
</script>
