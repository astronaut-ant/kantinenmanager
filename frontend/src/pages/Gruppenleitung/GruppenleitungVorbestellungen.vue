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

const calcCalendarEdges = () => {
  const range = 14;
  const hourOfOrderStop = 8;
  const startDate = new Date();
  const endDate = new Date(startDate);
  //added 1 for including the endDate itself
  endDate.setDate(endDate.getDate() + range + 1);
  const startTime = startDate.getHours();
  //no order possible after hour of orderstop
  // if (startTime >= hourOfOrderStop) {
  //   startDate.setDate(startDate.getDate() + 1);
  // }
  const startDateIso = startDate.toISOString().split("T")[0];
  const endDateIso = endDate.toISOString().split("T")[0];
  return { start: startDateIso, end: endDateIso };
};

const edges = calcCalendarEdges();

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
        validRange: {
          start: edges.start,
          end: edges.end,
        },
        events: [
          {
            start: "2024-12-21",
            end: "2024-12-21",
            color: "red",
            display: "background",
          },
        ],
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
