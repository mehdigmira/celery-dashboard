<template>
  <v-app light id="app">
    <munro-grid></munro-grid>
  </v-app>
</template>

<script>
  import MunroGrid from './components/TasksGrid';

  export default {
    name: 'app',
    data() {
      return {
      }
    },
    components: {
      TasksGrid,
    },
    methods: {

    }
  }
</script>

<style scoped>

</style>
