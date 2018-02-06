<template>
<div>
    <v-layout row justify-center>
    <v-dialog v-model="open" scrollable>
        <v-card>
          <v-toolbar color="primary" dark>
          <v-toolbar-title>Task {{ task.task_id }}</v-toolbar-title>
          <v-spacer></v-spacer>
        </v-toolbar>
          <v-card-text>
            <pre v-if="task.status == 'SUCCESS'" class="json-formatted">{{ task.result }}</pre>
            <pre v-else class="json-formatted">{{ task.traceback }}</pre>
          </v-card-text>
        </v-card>
    </v-dialog>
  </v-layout>
    </div>
</template>

<script>
import Vue from "vue";

export default {
  name: "task-dialog",
  props: ["openDialog", "task"],
  data() {
    return {
      open: false
    }
  },
  watch: {
    openDialog() {
      this.open = this.openDialog;
    },
    open(newV, oldV) {
      if (newV == false) {
        this.$emit("taskdialogclosed");
      }
    }
  },
  methods: {
  }
};
</script>