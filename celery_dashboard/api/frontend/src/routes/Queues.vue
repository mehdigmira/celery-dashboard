<template>
  <app-layout>
    <queues-grid></queues-grid>
  </app-layout>
</template>

<script>
  import AppLayout from '../components/AppLayout'
  import QueuesGrid from '../components/QueuesGrid'
  import { EventBus } from '../utils/bus.js'
  import 'whatwg-fetch';

  export default {
    name: 'queues',
    data() {
      return {
        runningPoller: null
      }
    },
    components: {
      AppLayout, QueuesGrid
    },
    methods: {

    },
    beforeRouteLeave (to, from, next) {
      EventBus.$emit("queuespolling", false)
      next()
    }
  }
</script>

<style scoped>

</style>
