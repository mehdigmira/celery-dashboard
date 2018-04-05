<template>
  <app-layout>
    <workers-grid></workers-grid>
  </app-layout>
</template>

<script>
  import AppLayout from '../components/AppLayout'
  import WorkersGrid from '../components/WorkersGrid'
  import { EventBus } from '../utils/bus.js'
  import 'whatwg-fetch';

  export default {
    name: 'workers',
    data() {
      return {
        runningPoller: null
      }
    },
    components: {
      AppLayout, WorkersGrid
    },
    methods: {

    },
    beforeRouteLeave (to, from, next) {
      EventBus.$emit("workerspolling", false)
      next()
    }
  }
</script>

<style scoped>

</style>
