<template>
  <v-snackbar
      :timeout="timeout"
      :color="color"
      v-model="open"
  >
    {{ text }}
    <v-btn dark flat @click.native="open = false">Close</v-btn>
  </v-snackbar>
</template>

<script>
  import { EventBus } from '../utils/bus.js';

  export default {
    name: 'snackbar',
    data () {
      return {
          timeout: null,
          color: null,
          open: false,
          text: null
      }
    },
    methods: {
        showSnackbar(data) {
            this.color = data.color;
            this.text = data.text;
            this.timeout = data.timeout;
            this.open = true;
        }
    },
    created() {
        EventBus.$on('snackbar:show', this.showSnackbar);  
    }
  }
</script>