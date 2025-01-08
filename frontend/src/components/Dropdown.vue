<template>
  <div class="text-start">
    <v-menu location="end">
      <template v-slot:activator="{ props }">
        <v-btn elevation="0" class="bg-transparent" v-bind="props">
          <v-icon class="me-1">{{ menuIcon }}</v-icon>
          {{ menuName }} <v-icon icon="mdi-menu-right" size="small"></v-icon>
        </v-btn>
      </template>

      <v-list class="bg-red">
        <v-list-item v-for="(item, index) in props.items" :key="index">
          <v-list-item-title
            ><v-btn elevation="0" class="bg-transparent" :to="item.link">
              <v-icon class="me-1">{{ item.icon }}</v-icon
              >{{ item.title }}</v-btn
            ></v-list-item-title
          >
        </v-list-item>
      </v-list>
    </v-menu>
  </div>
</template>

<script setup>
const props = defineProps(["items", "menuName", "menuIcon"]);
</script>
