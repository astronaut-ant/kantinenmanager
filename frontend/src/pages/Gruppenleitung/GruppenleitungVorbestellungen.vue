<template>
  <NavbarGruppenleitung :breadcrumbs="[{ title: 'Vorbestellungen' }]" />
  <h1 class="text-center mt-5 mb-7 text-blue-grey-darken-3">Vorbestellungen</h1>
  <div class="mx-auto w-75">
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
    <BestellFormular
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
    <BestellFormular />
  </div>
</template>

<script>
import FullCalendar from "@fullcalendar/vue3";
import dayGridPlugin from "@fullcalendar/daygrid";
import interactionPlugin from "@fullcalendar/interaction";
import CalendarDialog from "@/components/CalendarDialog.vue";
import deLocale from "@fullcalendar/core/locales/de";
import { useAppStore } from "@/stores/app.js";
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
let groupLeaderId;
let groupLocationId;
let groupData = {};
let employeeMap = {};

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
        weekends: false,
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
        allGroupsArray.push(group.group_name);
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
      console.log("SG", selectedGroup);
      console.log(groupLocationId);
      const initOrders = [];
      groupData.groups.forEach((group) => {
        if (group.group_name === selectedGroup) {
          group.employees.forEach((employee) => {
            initOrders.push({
              date: selectedDate,
              location_id: groupLocationId,
              date: selectedDate,
              main_dish: null,
              nothing: false,
              person_id: employee.id,
              salad_option: false,
            });
          });
        }
      });
      console.log("initOrders", initOrders);

      //Mockup Post for initializing new Bestellformular
      axios
        .post(
          `${import.meta.env.VITE_API}/api/pre-orders`,
          initOrders,
          {
            withCredentials: true,
          }
          // JSON.stringify({
          //   id: groupLeaderId,
          //   groups: groupData.groups,
          // })
        )
        .then(() => {
          this.calendarOptions.events = [];
          this.fillCalendar(groupLeaderId);
        })

        .catch((err) => {
          console.log(err);
        });
      setTimeout(() => {
        this.clickedEventDate = this.clickedDate;
        this.getOrdersByDate(selectedGroup);

        this.showBestellformular = true;
      }, 250);
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
      console.log("GETTING ORDERS BY DATE...");
      this.selectedGroup = clickedGroup;
      const ordersByDate = [];
      groupData.groups.forEach((group) => {
        if (group.group_name === clickedGroup) {
          group.orders.forEach((order) => {
            if (order.date === this.clickedEventDate) {
              ordersByDate.push(order);
            }
          });
        }
      });
      const items = [];
      console.log("ordersByDate", ordersByDate);
      //item Format
      ordersByDate.forEach((order) => {
        let hauptgericht1Value;
        let hauptgericht2Value;
        if (order.main_dish === null) {
          hauptgericht1Value = false;
          hauptgericht2Value = false;
        } else if (order.main_dish === "blau") {
          hauptgericht1Value = true;
          hauptgericht2Value = false;
        } else if (order.main_dish === "rot") {
          hauptgericht1Value = false;
          hauptgericht2Value = true;
        }
        items.push({
          name: employeeMap[order.person_id],
          person_id: order.person_id,
          hauptgericht1: hauptgericht1Value,
          hauptgericht2: hauptgericht2Value,
          salat: order.salad_option,
          keinEssen: order.nothing,
        });
        console.log("actual Orders:", items);
      });
      this.actualOrders = items;
    },

    updateBestellformular: function (updatedOrders, date, selectedGroup) {
      console.log(updatedOrders, date, selectedGroup);
      const formattedOrders = [];
      updatedOrders.forEach((updatedOrder) => {
        let dateValue = date;
        let maindishValue;
        if (updatedOrder.hauptgericht1) {
          maindishValue = "blau";
        } else if (updatedOrder.hauptgericht2) {
          maindishValue = "rot";
        } else {
          maindishValue = null;
        }
        formattedOrders.push({
          date: dateValue,
          location_id: groupLocationId,
          main_dish: maindishValue,
          salad_option: updatedOrder.salat,
          person_id: updatedOrder.person_id,
          nothing: updatedOrder.keinEssen,
        });
      });
      console.log(formattedOrders);
      // let filteredArray;
      // groupData.groups.forEach((group) => {
      //   if (group.groupName == selectedGroup) {
      //     filteredArray = group.groupOrders.filter((order) => {
      //       return order.date != date;
      //     });
      //     formattedOrders.forEach((fOrder) => {
      //       filteredArray.push(fOrder);
      //       group.groupOrders = filteredArray;
      //     });
      //     console.log("go on", groupData);
      //   }
      // });
      // console.log();

      axios
        .post(`${import.meta.env.VITE_API}/api/pre-orders`, formattedOrders, {
          withCredentials: true,
        })
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
          .get(
            `${import.meta.env.VITE_API}/api/pre-orders/by-group-leader/${id}`,
            {
              withCredentials: true,
            }
          )
          .then((response) => {
            groupData = response.data;
            console.log(groupData);
            const groupedEvents = [];
            employeeMap = {};
            groupData.groups.forEach((group) => {
              group.employees.forEach((employee) => {
                employeeMap[
                  employee.id
                ] = `${employee.first_name} ${employee.last_name}`;
              });
              groupedEvents.push({
                groupName: group.group_name,
                isHomegroup: group.is_home_group,
                groupOrderDatesList: this.getGroupDates(group.orders),
              });
            });
            console.log("GE!", groupedEvents);
            console.log(employeeMap);
            groupedEvents.forEach((groupedEvent) => {
              groupedEvent.groupOrderDatesList.forEach((groupOrderDate) => {
                console.log(groupedEvent.groupName, groupOrderDate);
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
    console.log(employeeMap);
    const appStore = useAppStore();
    groupLeaderId = appStore.userData.id;
    console.log("TEST");
    axios
      .get(`${import.meta.env.VITE_API}/api/groups`, {
        withCredentials: true,
      })
      .then((response) => {
        let ownGroup = response.data;
        groupLocationId = ownGroup[0].location.id;
      })
      .catch((err) => {
        console.log("NOT WORKING");
      });

    // groupLocationId = appStore.userData.location_id;
    console.log(appStore);
    this.fillCalendar(groupLeaderId);
  },
};
</script>

<style>
.fc-toolbar-title {
  color: #37474f !important;
}
.fc-day-today {
  background: #1866c037 !important;
  border: none !important;
}
.fc-day-today:hover {
  background: #e8f5e9 !important;
  border: none !important;
}

.fc-day:hover {
  background: #e8f5e9 !important;

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
  background-color: #e8f5e9 !important;
}

.fc-daygrid-day-number {
  pointer-events: none;
}
.fc-daygrid-day {
  height: 120px !important;
}
</style>
