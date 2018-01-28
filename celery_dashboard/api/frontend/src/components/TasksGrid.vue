<template>
<div>
  <task-dialog :open-dialog="openDialog" v-on:taskdialogclosed="taskDialogClosed" :task="taskToOpen"></task-dialog>
  <ag-grid-vue class="ag-theme-material grid"
               :gridOptions="gridOptions"
               :rowClicked="onRowClicked"
               :rowDataChanged="onRowDataChanged">
  </ag-grid-vue>

  <v-navigation-drawer
      temporary
      v-model="drawer"
      :mini-variant="mini"
      dark
      absolute
    >
      <v-list class="pa-1">
        <v-list-tile v-if="mini" @click.stop="mini = !mini">
          <v-list-tile-action>
            <v-icon>chevron_right</v-icon>
          </v-list-tile-action>
        </v-list-tile>
        <v-list-tile avatar tag="div">
          <v-list-tile-avatar>
            <img src="https://randomuser.me/api/portraits/men/85.jpg" />
          </v-list-tile-avatar>
          <v-list-tile-content>
            <v-list-tile-title>John Leider</v-list-tile-title>
          </v-list-tile-content>
          <v-list-tile-action>
            <v-btn icon @click.stop="mini = !mini">
              <v-icon>chevron_left</v-icon>
            </v-btn>
          </v-list-tile-action>
        </v-list-tile>
      </v-list>
    </v-navigation-drawer>

</div>
</template>

<script>

  import Vue from "vue";
  import {AgGridVue} from "ag-grid-vue";
  import 'whatwg-fetch';
  import Vuetify from 'vuetify';
  import TaskDialog from './TaskDialog';

  const moment = require("moment");

  const StatusChipComponent = Vue.extend({
    template: `<v-chip :color="getColor()" text-color="white">{{ params.value }}</v-chip>`,
    methods: {
      getColor() {
            let color = "primary"
            if (this.params.value == "QUEUED") color = "orange"
            if (this.params.value == "SUCCESS") color = "green"
            if (this.params.value == "FAILURE") color = "red"
            if (this.params.value == "RETRY") color = "indigo"    
            return color;
      }
    }
  })

  export default {
    name: 'munro-grid',
    data () {
      return {
        gridOptions: null,
        rowData: null,
        openDialog: false,
        taskToOpen: {}
      }
    },
    components: {
      AgGridVue,
      TaskDialog
    },
    methods: {
      taskDialogClosed() {
        this.openDialog = false;
      },
      loadRowData() {
        fetch('/api/tasks').then((response) => {
          return response.json()
        })
          .then((json) => {
            this.gridOptions.api.setRowData(json.result);
          });
      },
      createColDefs() {
        function toText(params) {
          return `<pre class="json-formatted">${JSON.stringify(params.data[params.colDef.field], null, 2)}</pre>`
        }

        return [
          {headerName: "Task", field: "name", width: 200, suppressSizeToFit: true},
          {headerName: "Queue", field: "routing_key", width: 150, suppressSizeToFit: true},
          {headerName: "Args", field: "args", cellRenderer: toText},
          {headerName: "Kwargs", field: "kwargs", cellRenderer: toText},
          {headerName: "Status", field: "status", width: 150, suppressSizeToFit: true, cellRendererFramework: StatusChipComponent},
          {
            headerName: "Date", field: "date_done", width: 180, cellRenderer(params) {
                let s = [];
                if (params.data.date_done) s.push("Done: " + moment.utc(params.data.date_done).fromNow())
                if (params.data.date_queued) s.push("Queued: " + moment.utc(params.data.date_queued).fromNow())
                if (params.data.eta) s.push("Eta: " + moment.utc(params.data.eta).fromNow())
            return `<pre class="simple-text">${s.join("\n")}</pre>`
          }
          },
        ];
      },
      onRowClicked(params) {
        this.$emit("munroSelected", params.node.data)
      },
      onRowDataChanged() {
        Vue.nextTick(() => {
            this.gridOptions.api.sizeColumnsToFit();
          }
        );
      }
    },
    created() {
      var self = this;
      this.gridOptions = {
        enableFilter: true,
        suppressCellClickSelection: true,
        enableColResize: true,
        getRowHeight(params) {
          return 120;
        },
        onRowDoubleClicked(row) {
          self.openDialog = true;
          self.taskToOpen = row.data;
        }
      };
      this.gridOptions.columnDefs = this.createColDefs();
      this.loadRowData();
    }
  }
</script>

<style>
  .grid {
    height: 1000px;
  }

  div.ag-root {
    -webkit-user-select: text;
    -moz-user-select: text;
    -ms-user-select: text;
    user-select: text;
  }

  pre.json-formatted {
    font-family: monospace;
    background-color: #F0F0F0;
    color: black;
    border: 1px solid #C0C0C0;
    font-size: 12px;
    padding: 9px;
    margin-top: 5px;
    line-height: 1.42857143;
    border-radius: 4px;
    height: auto;
    max-height: 200px;
    overflow: auto;
    background-color: #eeeeee;
    word-break: normal !important;
    word-wrap: normal !important;
    white-space: pre !important;
  }

  pre.simple-text {
    overflow: scroll;
    line-height: 1.42857143;
    word-break: break-all;
    word-wrap: break-word;
    padding-top: 10px;
  }
</style>
