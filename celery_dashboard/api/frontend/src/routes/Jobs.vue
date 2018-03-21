<template>
  <app-layout>
    <tasks-grid></tasks-grid>
  </app-layout>
</template>

<script>
  import TasksGrid from '../components/TasksGrid';
  import AppLayout from '../components/AppLayout'

  export default {
    name: 'jobs',
    data() {
      return {
      }
    },
    components: {
      TasksGrid,
      AppLayout
    },
    methods: {

    }
  }
</script>

<style scoped>

</style>
