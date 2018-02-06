<template>
  <v-app light id="app">
    <side-menu></side-menu>
    <tasks-grid></tasks-grid>
  </v-app>
</template>

<script>
  import TasksGrid from './components/TasksGrid';
  import SideMenu from './components/SideMenu';

  export default {
    name: 'app',
    data() {
      return {
      }
    },
    components: {
      TasksGrid,
      SideMenu
    },
    methods: {

    }
  }
</script>

<style scoped>

</style>
