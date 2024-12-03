<template>
  <NavbarStandort></NavbarStandort>
  <v-container max-width="1600" class="d-flex justify-center">
    <div class="mx-4 my-5 d-flex justify-start flex-wrap">
      <GroupCard
        v-for="group in groups"
        :id="group.id"
        :name="group.name"
        :loaction="group.loaction"
        :group_leader="group.group_leader"
        :number="group.number"
      />
    </div>
  </v-container>
</template>

<script setup>


const groups = [
    {
        id: '95f0534f-1580-4d09-8573-8b419d7dc1df',
        name: 'Montage/Verpackung 1 - W1',
        loaction: 'W1',
        group_leader: 'Herr x/Frau x',
        number: '10001'
    },
    {
        id: '6284b2d9-8ad3-4945-9969-e2c5c1bae017',
        name: 'Montage/Verpackung 2 - W2',
        loaction: 'W2',
        group_leader: 'Herr y/Frau y',
        number: '10002'
    },
    {
        id: '833635f1-ffc1-4b60-ae60-d5f71dad85bc',
        name: 'Montage/Verpackung 3 - W3',
        loaction: 'W3',
        group_leader: 'Herr z/Frau z',
        number: '100'
    },
    {
        id: 'eb3bb231-8e58-41f3-aee2-2a0e3501f68d',
        name: 'Montage/Verpackung 4 - W4',
        loaction: 'W4',
        group_leader: 'Herr a/Frau a',
        number: '10004'
    },
    {
        id: 'eb3bb231-8e58-41f3-aee2-2a0e3501f68d',
        name: 'Montage',
        loaction: 'W4',
        group_leader: 'Herr a',
        number: '1000400000000000000'
    },
];


</script>
