<template>
  <NavbarStandort></NavbarStandort>
  <GroupLeaderCard
    v-for="groupleader in groupleaders"
    :id="groupleader.id"
    :name="groupleader.name"
    :loaction="groupleader.loaction"
    :group="groupleader.group"
    :anwesend="groupleader.anwesend">

  </GroupLeaderCard>
</template>
  
<script setup>
  const groupleaders = [
    {
        id: '95f0534f-1580-4d09-8573-8b419d7dc1df',
        name: 'Herr Müller',
        loaction: 'W1',
        group: 'W1',
        anwesend: false
    },
    {
        id: '95f0534f-1580-4d09-8573-8b419d7dc1df',
        name: 'Herr Müller',
        loaction: 'W1',
        group: 'W1',
        anwesend: true
    },
  ];
</script>
  