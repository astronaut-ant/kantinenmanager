<template>
  <NavbarGruppenleitung />
  <h1 class="text-center mt-5 mb-5">Vorbestellungen</h1>
  <div class="ps-10 pe-10">
    <FullCalendar :options="calendarOptions" />
    <CalendarDialog
      v-if="showDialog"
      :showDialog="showDialog"
      :date="clickedDate"
      :groups="possibleGroupsChoice"
      @close="this.showDialog = false"
      @init="initNewBestellformular"
      :stopHour="stopHour"
    />
    <Bestellformular
      v-if="showBestellformular"
      :date="clickedEventDate"
      :showBestellformular="showBestellformular"
      :orders="actualOrders"
      :group="selectedGroup"
      @save="updateBestellformular"
      @close="showBestellformular = false"
      @restore="showBestellformular = true"
      :stopHour="stopHour"
    />
  </div>
</template>

<script>
import FullCalendar from "@fullcalendar/vue3";
import dayGridPlugin from "@fullcalendar/daygrid";
import interactionPlugin from "@fullcalendar/interaction";
import CalendarDialog from "@/components/CalendarDialog.vue";
import Bestellformular from "@/components/Bestellformular.vue";
import deLocale from "@fullcalendar/core/locales/de";
import axios from "axios";

//Non reactive

const calcCalendarEdges = () => {
  const range = 14;
  const startDate = new Date();
  const hintDate = new Date(startDate);
  hintDate.setDate(hintDate.getDate() + range);
  //added 1 for including the hintDate itself
  const endDate = new Date(hintDate);
  endDate.setDate(endDate.getDate() + 1);
  const startTime = startDate.getHours();
  const startDateIso = startDate.toISOString().split("T")[0];
  const hintDateIso = hintDate.toISOString().split("T")[0];
  const endDateIso = endDate.toISOString().split("T")[0];
  return { start: startDateIso, hint: hintDateIso, end: endDateIso };
};
const edges = calcCalendarEdges();
const groupLeaderId = 1;
let groupData = {};

//reactive

export default {
  components: {
    FullCalendar, // make the <FullCalendar> tag available
  },
  data() {
    return {
      possibleGroupsChoice: [],
      stopHour: 8,
      showDialog: false,
      showBestellformular: false,
      clickedDate: "",
      clickedEventDate: "",
      selectedGroup: "",
      actualOrders: [],
      calendarOptions: {
        plugins: [dayGridPlugin, interactionPlugin],
        headerToolbar: {
          start: "title",
          center: "",
          end: "",
        },
        height: "auto",
        views: {
          timeGrid2Weeks: {
            type: "dayGridMonth",
            duration: { weeks: 3 },
          },
        },
        initialView: "timeGrid2Weeks",
        fixedWeekCount: false,
        locale: deLocale,
        dateClick: this.handleDateClick,
        eventClick: this.handleEventClick,
        validRange: {
          start: edges.start,
          end: edges.end,
        },
        visibleRange: {
          start: edges.start,
          end: edges.end,
        },
        events: [],
        eventContent: function (arg) {
          // console.log(arg.event.title);
          return {
            html: `<div style='padding-left: 5px;'><h5 style='white-space: wrap !important;word-break: break-word;text-align: start; width:100%'>${arg.event.title}</h5></div>`,
          };
        },
      },
    };
  },
  methods: {
    handleDateClick: function (arg) {
      //alert("date click! " + arg.dateStr);
      const allGroupsArray = [];
      const existingEventsOnDay = [];
      groupData.groups.forEach((group) => {
        allGroupsArray.push(group.groupName);
      });

      this.calendarOptions.events.forEach((event) => {
        if (event.display != "background" && event.date === arg.dateStr) {
          existingEventsOnDay.push(event.title);
        }
      });
      console.log(allGroupsArray);
      console.log(existingEventsOnDay);
      let intersect = allGroupsArray.filter((group) => {
        return !existingEventsOnDay.includes(group);
      });
      this.possibleGroupsChoice = intersect;
      console.log(intersect);
      this.showDialog = true;
      this.clickedDate = arg.dateStr;
    },
    handleEventClick: function (arg) {
      const rawClickedEventDate = new Date(arg.event.start);
      rawClickedEventDate.setDate(rawClickedEventDate.getDate() + 1);
      this.clickedEventDate = rawClickedEventDate.toISOString().split("T")[0];
      console.log(this.clickedEventDate);

      this.getOrdersByDate(arg.event.title);

      if (arg.event.display != "background") {
        this.showBestellformular = true;
      }
    },
    initNewBestellformular: function (selectedGroup, selectedDate) {
      console.log(selectedGroup);
      groupData.groups.forEach((group) => {
        if (group.groupName === selectedGroup) {
          group.groupEmployees.forEach((employee) => {
            group.groupOrders.push({
              name: employee,
              date: selectedDate,
              maindish: 0,
              salad: false,
              nothing: false,
              done: false,
            });
          });
        }
      });
      console.log(groupData.groups);

      //Mockup Post for initializing new Bestellformular
      axios
        .put(
          "http://localhost:4000/groupOrdersByPersonId/" + groupLeaderId,
          JSON.stringify({
            id: groupLeaderId,
            groups: groupData.groups,
          })
        )
        .then(() => {
          this.calendarOptions.events = [];
          this.fillCalendar(groupLeaderId);
          this.getOrdersByDate(selectedGroup);
        });

      this.clickedEventDate = this.clickedDate;
      setTimeout(() => {
        this.showBestellformular = true;
      }, "250");
    },
    //Helper
    getGroupDates: function (groupOrders) {
      const dateList = [];
      groupOrders.forEach((order) => {
        dateList.push(order.date);
      });
      return [...new Set(dateList)];
    },
    getOrdersByDate: function (clickedGroup) {
      this.selectedGroup = clickedGroup;
      const ordersByDate = [];
      groupData.groups.forEach((group) => {
        if (group.groupName === clickedGroup) {
          group.groupOrders.forEach((order) => {
            if (order.date === this.clickedEventDate) {
              ordersByDate.push(order);
            }
          });
        }
      });
      const items = [];
      //item Format
      ordersByDate.forEach((order) => {
        let hauptgericht1Value;
        let hauptgericht2Value;
        if (order.maindish === 0) {
          hauptgericht1Value = false;
          hauptgericht2Value = false;
        } else if (order.maindish === 1) {
          hauptgericht1Value = true;
          hauptgericht2Value = false;
        } else if (order.maindish === 2) {
          hauptgericht1Value = false;
          hauptgericht2Value = true;
        }
        items.push({
          name: order.name,
          hauptgericht1: hauptgericht1Value,
          hauptgericht2: hauptgericht2Value,
          salat: order.salad,
          keinEssen: order.nothing,
          done: order.done,
        });
      });
      this.actualOrders = items;
    },

    updateBestellformular: function (updatedOrders, date, selectedGroup) {
      //fehlt noch gruppe
      console.log(updatedOrders, date, selectedGroup);
      const formattedOrders = [];
      updatedOrders.forEach((updatedOrder) => {
        let dateValue = date;
        let maindishValue;
        if (updatedOrder.hauptgericht1) {
          maindishValue = 1;
        } else if (updatedOrder.hauptgericht2) {
          maindishValue = 2;
        } else {
          maindishValue = 0;
        }
        formattedOrders.push({
          name: updatedOrder.name,
          date: dateValue,
          maindish: maindishValue,
          salad: updatedOrder.salat,
          nothing: updatedOrder.keinEssen,
          done: updatedOrder.done,
        });
      });
      console.log(formattedOrders);
      let filteredArray;
      groupData.groups.forEach((group) => {
        if (group.groupName == selectedGroup) {
          filteredArray = group.groupOrders.filter((order) => {
            return order.date != date;
          });
          formattedOrders.forEach((fOrder) => {
            filteredArray.push(fOrder);
            group.groupOrders = filteredArray;
          });
          console.log("go on", groupData);
        }
      });
      console.log();
      axios
        .put(
          "http://localhost:4000/groupOrdersByPersonId/" + groupLeaderId,
          JSON.stringify({
            id: groupLeaderId,
            groups: groupData.groups,
          })
        )
        .then(() => {
          this.calendarOptions.events = [];
          this.fillCalendar(groupLeaderId);
        });

      this.showBestellformular = false;
    },
    fillCalendar: function (id) {
      this.calendarOptions.events.push({
        start: edges.hint,
        end: edges.hint,
        color: "#F44336",
        display: "background",
      }),
        axios
          .get(`http://localhost:4000/groupOrdersByPersonId/${id}`)
          .then((response) => {
            groupData = response.data;
            const groupedEvents = [];
            groupData.groups.forEach((group) => {
              groupedEvents.push({
                groupName: group.groupName,
                isHomegroup: group.isHomegroup,
                groupOrderDatesList: this.getGroupDates(group.groupOrders),
              });
            });
            console.log(groupedEvents);
            groupedEvents.forEach((groupedEvent) => {
              groupedEvent.groupOrderDatesList.forEach((groupOrderDate) => {
                this.calendarOptions.events.push({
                  title: groupedEvent.groupName,
                  date: groupOrderDate,
                  backgroundColor: groupedEvent.isHomegroup
                    ? "#1867C0"
                    : "#F44336",
                  borderColor: groupedEvent.isHomegroup ? "#1867C0" : "#F44336",
                });
              });
            });
          })
          .catch((err) => console.log(err));
    },
  },
  mounted: function () {
    this.fillCalendar(groupLeaderId);
  },
};
</script>

<style>
.fc-day-today {
  background: #1866c037 !important;
  border: none !important;
}
.fc-day-today:hover {
  background: #fff9c4 !important;
  border: none !important;
}

.fc-day:hover {
  background: #fff9c4 !important;
  cursor: pointer;
}
.fc-event:hover {
  padding: 1px;
}

.fc-col-header-cell:hover {
  background: white !important;
  cursor: auto;
}

.fc-day-disabled:hover {
  background: rgb(241, 241, 241) !important;
  cursor: auto;
}

.fc-bg-event:hover {
  background-color: #fff9c4 !important;
}

.fc-daygrid-day-number {
  pointer-events: none;
}
.fc-daygrid-day {
  height: 120px !important;
}
</style>
