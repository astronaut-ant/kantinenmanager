<template>
    <div class="mt-4">
      <div v-if="isPinned" class="mt-4" :style="{ height: `${height}px`, width: '100%' }"></div>
      
      <div 
        class="d-flex justify-center align-center sticky-header mt-4"
        :class="{ pinned: isPinned, transitioning: isTransitioning }"
        :style="isPinned ? { transform: `translateY(${translateY}px)` } : ''"
      >
        <v-toolbar border color="white" density="comfortable" style="max-width: 800px;" rounded="lg" floating>
          <div v-if="props.viewSwitcherEnabled" class="d-flex align-center flex-column ml-6 mr-6">
            <v-btn-toggle v-model="ansicht" variant="outlined" base-color="black" color="primary" mandatory divided density="comfortable" @update:modelValue="onToggleChange">
              <v-btn
                icon="mdi-card-outline"
                value="cardview"
              ></v-btn>
              <v-btn
                icon="mdi-table"
                value="tableview"
              ></v-btn>
            </v-btn-toggle>
          </div>
          <v-divider v-if="props.viewSwitcherEnabled" inset vertical></v-divider>
          <v-text-field
            class="ml-6 mr-6"
            v-model="search"
            density="compact"
            label="Suche"
            prepend-inner-icon="mdi-magnify"
            variant="solo-filled"
            flat
            hide-details
            single-line
            clearable
            rounded="xl"
          ></v-text-field>
        </v-toolbar>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted, onUnmounted } from "vue";

  const props = defineProps(["items", "viewSwitcherEnabled", "filterList"]);
  const emit = defineEmits(["searchresult", "changeview"]);

  const ansicht = ref("cardview");
  const search = ref("");
  
  const isPinned = ref(false);
  const isTransitioning = ref(false);
  const translateY = ref(0); 
  const lastScrollY = ref(window.scrollY);
  const height = ref(0); 
  
  const handleScroll = () => {
    const currentScrollY = window.scrollY;
  
    if (currentScrollY > lastScrollY.value && currentScrollY > height.value) {
      isPinned.value = true;
      isTransitioning.value = false;
      translateY.value = 0;
    }
    else if (currentScrollY < lastScrollY.value && currentScrollY > height.value) {
      isPinned.value = true;
      isTransitioning.value = false;
    }
    else if (currentScrollY < lastScrollY.value && currentScrollY <= height.value) {
      isPinned.value = false;
      isTransitioning.value = false;
      translateY.value = 0;
    }
  
    lastScrollY.value = currentScrollY;
  };
  
  onMounted(() => {
    const element = document.querySelector(".sticky-header");
    height.value = element.offsetHeight;
  
    window.addEventListener("scroll", handleScroll);
  });
  
  onUnmounted(() => {
    window.removeEventListener("scroll", handleScroll);
  });
  const filteredUsers = computed(() => {
      if (!search.value) {
          return Object.values(props.items);
      }

      const searchTerm = search.value.toLowerCase();

      return Object.values(props.items).filter((user) =>
        props.filterList.some((key) =>
              user[key]?.toLowerCase().includes(searchTerm)
          )
      );
  });


  watch(filteredUsers, (newFilteredUsers) => {
    emit("searchresult", newFilteredUsers);
  });

  const onToggleChange = (newValue) => {
    emit('changeview', newValue);
  };
  </script>
  

<style scoped>
  .sticky-header {
    position: relative;
    z-index: 10;
    transition: transform 0.3s ease;
  }
  
  .sticky-header.pinned {
    position: fixed;
    top: 0;
    width: 100%;
  }
  
  .sticky-header.transitioning {
    transition: transform 0.2s ease;
  }
</style>
  