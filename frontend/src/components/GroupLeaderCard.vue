<template>
  <v-card
    class="mx-2 my-2 text-blue-grey-darken-2 w-xs-25 w-md-100"
    min-width="350"
    max-width="350"
    elevation="16"
  >
    <v-card-item>
      <div class="mb-2 d-flex justify-center">
        <v-chip
          :color="
            props.available_group_leaders.some(
              (leader) => leader.id === props.id
            )
              ? 'green'
              : 'red'
          "
          class="text-uppercase d-flex justify-center flex-grow-1"
          size="small"
          label
        >
          <v-icon
            class="me-2"
            v-if="
              props.available_group_leaders.some(
                (leader) => leader.id === props.id
              )
            "
            >mdi-calendar-check-outline</v-icon
          >
          <v-icon class="me-2" v-else>mdi-calendar-remove-outline</v-icon>
          {{
            props.available_group_leaders.some(
              (leader) => leader.id === props.id
            )
              ? "verfügbar"
              : "abwesend"
          }}
        </v-chip>
      </div>
      <div>
        <div>
          <v-card-title class="mb-2"
            >Gruppenleiter: {{ props.first_name }}
            {{ props.last_name }}</v-card-title
          >
          <v-slide-group :mobile="false">
            <v-slide-group-item>
              <v-chip color="primary" class="mr-2" size="small" label>
                <v-icon icon="mdi-account-group" class="me-2"></v-icon>
                <span
                  >Hauptgruppe: {{ props.own_group?.group_name || "-" }}</span
                >
              </v-chip>
            </v-slide-group-item>
            <v-slide-group-item v-for="replacement_group in replacement_groups">
              <v-chip color="orange" class="mr-2" size="small" label>
                <v-icon class="me-2">mdi-calendar-clock-outline</v-icon>
                Vertretung für {{ replacement_group.group_name }}
              </v-chip>
            </v-slide-group-item>
          </v-slide-group>
        </div>
      </div>
    </v-card-item>
    <v-card-text>
      <v-divider></v-divider>
      <div class="mt-3 d-flex justify-end">
        <v-btn
          v-if="
            props.available_group_leaders.some(
              (leader) => leader.id === props.id
            )
          "
          :disabled="
            props.replacement_groups.length > 0 || props.own_group === null
          "
          color="red"
          @click="opensetGroupReplacementDialog"
          size="small"
          flat
          variant="outlined"
          >Als Abwesend markieren</v-btn
        >
        <v-btn
          v-else
          color="primary"
          @click="openremoveGroupReplacementDialog"
          size="small"
          flat
          variant="outlined"
          >Als Anwesend markieren</v-btn
        >
      </div>
    </v-card-text>
  </v-card>
  <v-dialog v-model="setGroupReplacementDialog" persistent max-width="500">
    <v-card>
      <v-card-text>
        <div class="d-flex text-primary mb-7">
          <p class="text-h5 mt-1 font-weight-black">Vertretung setzen</p>
        </div>
        <div class="text-medium-emphasis mb-7">
          <p>
            Bitte wählen Sie einen neuen Gruppenleiter, der für die Gruppe
            <strong>{{ props.own_group?.group_name }}</strong>
            Essensbestellungen übernehmen kann.
          </p>
        </div>
        <v-select
          :active="true"
          base-color="blue-grey"
          color="primary"
          variant="outlined"
          placeholder="Gruppenleiter auswählen"
          Label="Gruppenleiter"
          v-model="replacementGroupLeader"
          :items="trueavailable_group_leaders.value"
          item-title="full_name"
          item-value="id"
          label="Gruppenleiter"
        ></v-select>
        <v-alert
          color="red"
          icon="mdi-alert-outline"
          text="Der aktuelle Gruppenleiter kann bis zu seiner Rückkehr keine Bestellungen für seine Gruppe vornehmen."
          density="compact"
        ></v-alert>
      </v-card-text>
      <v-card-actions>
        <v-btn text @click="closesetGroupReplacementDialog">Abbrechen</v-btn>
        <v-btn
          color="primary"
          variant="elevated"
          @click="confirmSetGroupReplacement"
          >Vertretung setzen</v-btn
        >
      </v-card-actions>
    </v-card>
  </v-dialog>

  <v-dialog v-model="removeGroupReplacementDialog" persistent max-width="500">
    <v-card>
      <v-card-text>
        <div class="d-flex justify-center text-primary mb-7">
          <p class="text-h5 font-weight-black">Vertretung löschen</p>
        </div>
        <div class="text-medium-emphasis">
          <p>
            Durch das Entfernen der Vertretung kann
            <strong>{{ props.first_name }} {{ props.last_name }}</strong> wieder
            Essensbestellungen für die Gruppe
            <strong>{{ props.own_group?.group_name }}</strong> übernehmen.
          </p>
        </div>
      </v-card-text>
      <v-card-actions>
        <v-btn text @click="closeremoveGroupReplacementDialog">Abbrechen</v-btn>
        <v-btn
          color="primary"
          variant="elevated"
          @click="removeGroupReplacement"
          >Vertretung löschen</v-btn
        >
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { useFeedbackStore } from "@/stores/feedback";
const feedbackStore = useFeedbackStore();
const replacementGroupLeader = ref("");
const setGroupReplacementDialog = ref(false);
const removeGroupReplacementDialog = ref(false);
const trueavailable_group_leaders = ref([]);
const props = defineProps([
  "id",
  "first_name",
  "last_name",
  "own_group",
  "replacement_groups",
  "available_group_leaders",
]);
const emit = defineEmits(["replacement-set", "replacement-removed"]);

import axios from "axios";

trueavailable_group_leaders.value = computed(() => {
  return props.available_group_leaders.filter(
    (leader) => leader.id !== props.id
  );
});

const removeGroupReplacement = () => {
  axios
    .delete(
      `${import.meta.env.VITE_API}/api/groups/remove-replacement/${
        props.own_group?.id
      }`,
      { withCredentials: true }
    )
    .then(() => {
      emit("replacement-removed");
      closeremoveGroupReplacementDialog();
      feedbackStore.setFeedback(
        "success",
        "snackbar",
        "Vertretung gelöscht",
        "Der Gruppenleiter kann wieder Essensbestellungen für seine Gruppe übernehmen."
      );
    })
    .catch((err) => {
      feedbackStore.setFeedback(
        "error",
        "snackbar",
        err.response?.data?.title,
        err.response?.data?.description
      );
    });
};
const opensetGroupReplacementDialog = () => {
  setGroupReplacementDialog.value = true;
};

const closesetGroupReplacementDialog = () => {
  setGroupReplacementDialog.value = false;
};

const openremoveGroupReplacementDialog = () => {
  removeGroupReplacementDialog.value = true;
};

const closeremoveGroupReplacementDialog = () => {
  removeGroupReplacementDialog.value = false;
};

const confirmSetGroupReplacement = () => {
  if (!replacementGroupLeader) {
    console.error("No group leader selected");
    return;
  }
  axios
    .put(
      `${import.meta.env.VITE_API}/api/groups/${props.own_group?.id}`,
      {
        group_number: props.own_group?.group_number,
        group_name: props.own_group?.group_name,
        location_id: props.own_group?.location_id,
        user_id_group_leader: props.id,
        user_id_replacement: replacementGroupLeader.value,
      },
      { withCredentials: true }
    )
    .then(() => {
      emit("replacement-set");
      closesetGroupReplacementDialog();
      feedbackStore.setFeedback(
        "success",
        "snackbar",
        "Vertretung gesetzt",
        "Der temporäre Gruppenleiter übernimmt Essensbestellungen für die Gruppe."
      );
    })
    .catch((err) => {
      closesetGroupReplacementDialog();
      feedbackStore.setFeedback(
        "error",
        "dialog",
        err.response?.data?.title,
        err.response?.data?.description
      );
    });
};
</script>

<style>
.v-slide-group__prev,
.v-slide-group__next {
  min-width: 30px;
  max-width: 30px;
}
</style>
