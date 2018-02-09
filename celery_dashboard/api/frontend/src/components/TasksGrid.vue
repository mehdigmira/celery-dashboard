<template>
<div>
  <v-snackbar
      :timeout="snackbar.timeout"
      :color="snackbar.color"
      v-model="snackbar.open"
  >
    {{ snackbar.text }}
    <v-btn dark flat @click.native="snackbar.open = false">Close</v-btn>
  </v-snackbar>
  <div class="filter-box">
    <v-form ref="form">
      <v-layout row wrap>
        <v-text-field
          label="Id"
          v-model="filters.taskId"
        ></v-text-field>
        <v-text-field
          label="Task"
          v-model="filters.task"
        ></v-text-field>
        <v-text-field
          label="Queue"
          v-model="filters.queue"
        ></v-text-field>
        <v-select
          label="Status"
          v-model="filters.status"
          :items="['ALL', 'QUEUED', 'STARTED', 'RETRY', 'SUCCESS', 'FAILURE']"
        ></v-select>
        <v-text-field
          label="Exception"
          v-model="filters.exception"
        ></v-text-field>
        <v-btn color="success" @click="filterData()">
          <v-icon left dark>filter_list</v-icon> Filter
        </v-btn>
        <v-menu
            transition="slide-y-transition"
            bottom
        >
          <v-btn color="primary" dark slot="activator" class="purple">
            <v-icon left dark>touch_app</v-icon> Action
          </v-btn>
          <v-list>
            <v-list-tile @click="cancelAll()">
              <v-list-tile-title>
              <v-icon left dark color="error">delete_forever</v-icon> Cancel these jobs
              </v-list-tile-title>
            </v-list-tile>
            <v-list-tile @click="requeueAll()">
              <v-list-tile-title>
              <v-icon left dark  color="success">replay</v-icon> Requeue these jobs
              </v-list-tile-title>
            </v-list-tile>
          </v-list>
          </v-menu>
      </v-layout>
    </v-form>
  </div>
  <task-dialog :open-dialog="openDialog" v-on:taskdialogclosed="taskDialogClosed" :task="taskToOpen"></task-dialog>
  <ag-grid-vue class="ag-theme-material grid"
               :gridOptions="gridOptions">
  </ag-grid-vue>
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
    template: `
              <div>
                <div>
                  <v-chip :color="getColor()" text-color="white">{{ params.value }}</v-chip>
                </div>
                <div>
                  <v-tooltip left>
                    <v-btn outline small fab color="red" @click="revoke()" slot="activator">
                      <v-icon dark>delete_forever</v-icon>
                    </v-btn>
                    <span>Cancel job</span>
                  </v-tooltip>
                  <v-tooltip right>
                    <v-btn outline small fab color="success" @click="requeue()" slot="activator">
                      <v-icon dark>replay</v-icon>
                    </v-btn>
                    <span>Requeue job</span>
                  </v-tooltip>
                </div>
              </div>
              `,
    methods: {
      getColor() {
        console.log(this.params.data.task_id);
            let color = "primary";
            if (this.params.value == "QUEUED") color = "orange";
            if (this.params.value == "SUCCESS") color = "green";
            if (this.params.value == "FAILURE") color = "red";
            if (this.params.value == "RETRY") color = "indigo";
            return color;
      },
      revoke() {
        fetch(`/api/task/${this.params.data.task_id}/revoke`).then((response) => {
              if (response.status !== 200) return this.params.context.componentParent.showSnackbar("An error occurred", "error", 2000);
              return this.params.context.componentParent.showSnackbar("Task successfully cancelled", "success", 2000);
        });
      },
      requeue() {
        fetch(`/api/task/${this.params.data.task_id}/requeue`).then((response) => {
              if (response.status !== 200) return this.params.context.componentParent.showSnackbar("An error occurred", "error", 2000);
              return this.params.context.componentParent.showSnackbar("Task successfully queued", "success", 2000);
        });
      }
    }
  });

  export default {
    name: 'tasks-grid',
    data () {
      return {
        loading: false,
        gridOptions: null,
        rowData: null,
        openDialog: false,
        taskToOpen: {},
        snackbar: {
          timeout: null,
          color: null,
          open: false
        },
        filters: {
          task: this.$route.query.task,
          status: this.$route.query.status,
          taskId: this.$route.query.taskId,
          queue: this.$route.query.queue,
          exception: this.$route.query.exception
        }
      }
    },
    components: {
      AgGridVue,
      TaskDialog
    },
    methods: {
      showSnackbar(text, color, timeout) {
        this.snackbar.color = color;
        this.snackbar.text = text;
        this.snackbar.timeout = timeout;
        this.snackbar.open = true;
      },
      cancelAll() {
        let filters = {};
        let self = this;
        Object.keys(this.filters).forEach((filter) => {
          let val = this.filters[filter];
          if (!!val && (filter !== "status" || val !== "ALL")) filters[filter] = val;
        });
        fetch('/api/tasks', {
          method: 'DELETE',
            headers: {
              'Content-Type': 'application/json'
            },
          body: JSON.stringify(filters)
        }).then((response) => {
            if (response.status !== 200) return self.showSnackbar("An error occurred", "error", 2000);
            return response.json();
        }).then(function (json) {
          return self.showSnackbar(`${json.count} task(s) successfully cancelled`, "success", 2000);
        })
      },
      requeueAll() {
        let filters = {};
        let self = this;
        Object.keys(this.filters).forEach((filter) => {
          let val = this.filters[filter];
          if (!!val && (filter !== "status" || val !== "ALL")) filters[filter] = val;
        });
        fetch('/api/tasks', {
          method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
          body: JSON.stringify(filters)
        }).then((response) => {
            if (response.status !== 200) return self.showSnackbar("An error occurred", "error", 2000);
            return response.json();
        }).then(function (json) {
          return self.showSnackbar(`${json.count} task(s) successfully requeued`, "success", 2000);
        })
      },
      filterData() {
        this.$router.push({path: "jobs", query: this.filters});
        this.gridOptions.api.setDatasource(this.getDatasource(this.gridOptions.api));
      },
      taskDialogClosed() {
        this.openDialog = false;
      },
      createColDefs() {
        function toText(params) {
            if (params.value !== undefined) {
              return `<pre class="json-formatted">${JSON.stringify(params.data[params.colDef.field], null, 2)}</pre>`;
            }
        }
        return [
          {headerName: "Task", field: "name", width: 200, suppressSizeToFit: true},
          {headerName: "Queue", field: "routing_key", width: 150, suppressSizeToFit: true},
          {headerName: "Args", field: "args", cellRenderer: toText, suppressSorting: true},
          {headerName: "Kwargs", field: "kwargs", cellRenderer: toText, suppressSorting: true},
          {headerName: "Status", field: "status", width: 150, suppressSizeToFit: true, cellRendererFramework: StatusChipComponent, cellClass: ['centered-cell']},
          {
            headerName: "Date", field: "date_done", width: 180, cellRenderer(params) {
                if (params.value !== undefined) {
                  let s = [];
                  if (params.data.date_done) s.push("Done: " + moment.utc(params.data.date_done).fromNow())
                  if (params.data.date_queued) s.push("Queued: " + moment.utc(params.data.date_queued).fromNow())
                  if (params.data.eta) s.push("Eta: " + moment.utc(params.data.eta).fromNow())
                  return `<pre class="simple-text">${s.join("\n")}</pre>`
                }
            }
          }
        ];
      },
      getFiltersParams() {
        let filtersArr = [];
        Object.keys(this.filters).forEach((param) => {
          let val = this.filters[param];
          if (!!val && (param !== "status" || val !== "ALL")) filtersArr.push(`${param}=${val}`);
        });
        return filtersArr
      },
      getDatasource(api) {
        let self = this;
        return {
          rowCount: null, // behave as infinite scroll
          getRows: function(params) {
            let sorts = [];
            params.sortModel.forEach((model) => {
              sorts.push(`${model.colId}:${model.sort}`)
            });
            let filters = self.getFiltersParams();
            let apiRoute = `/api/tasks?start=${params.startRow}&end=${params.endRow}&sort=${sorts.join(',')}`
            if (filters != "") apiRoute += `&${filters.join("&")}`;
            fetch(apiRoute).then((response) => {
              return response.json()
            })
            .then((json) => {
              params.successCallback(json.result, json.count);
              Vue.nextTick(() => {
                api.sizeColumnsToFit();
              });
            });
          }
        }
      }
    },
    beforeMount() {
      let self = this;
      this.gridOptions = {
        context: {
          componentParent: self
        },
        enableServerSideSorting: true,
        enableServerSideFilter: false,
        suppressFilter: true,
        enableColResize: true,
        rowDeselection: true,
        rowModelType: 'infinite',
        cacheOverflowSize: 2,
        maxConcurrentDatasourceRequests: 2,
        infiniteInitialRowCount: 0,
        maxBlocksInCache: 10000,
        pagination: true,
        paginationAutoPageSize: true,
        cacheBlockSize: 1000,
        suppressCellClickSelection: true,
        onGridReady() {
          let api = this.api;
          api.setDatasource(self.getDatasource(api));
        },
        rowHeight: 120,
        onRowDoubleClicked(row) {
          self.openDialog = true;
          self.taskToOpen = row.data;
        },
        columnDefs: this.createColDefs()
      };
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

  .filter-box {
    margin: 5px;
  }

  .filter-box .layout.wrap {
    align-items: center;
  }

  .filter-box .input-group {
    margin: 0 3px;
  }

  .centered-cell {
    text-align: center;
  }

  .filter-box .btn {
    margin-top: 0px;
  }
</style>
