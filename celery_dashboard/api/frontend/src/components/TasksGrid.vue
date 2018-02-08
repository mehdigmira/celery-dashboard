<template>
<div>
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
    name: 'tasks-grid',
    data () {
      return {
        loading: false,
        gridOptions: null,
        rowData: null,
        openDialog: false,
        taskToOpen: {},
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
      filterData() {
        this.$router.push({path: "jobs", query: this.filters})
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
          {headerName: "Status", field: "status", width: 150, suppressSizeToFit: true, cellRendererFramework: StatusChipComponent, filter:'agTextColumnFilter', filterParams: {
            applyButton: true, clearButton: true, filterOptions: ["equals"], textFormatter(s) { return s.toUpperCase() }
          }},
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
          },
        ];
      },
      getDatasource(api) {
        var self = this
        return {
          rowCount: null, // behave as infinite scroll 
          getRows: function(params) {
            let sorts = []
            params.sortModel.forEach((model) => {
              sorts.push(`${model.colId}:${model.sort}`)
            })
            let filters = ""
            Object.keys(self.filters).forEach((param) => {
              let val = self.filters[param]
              if (!!val && (param !== "status" || val !== "ALL")) filters += `&${param}=${val}`
            });
            let apiRoute = `/api/tasks?start=${params.startRow}&end=${params.endRow}&sort=${sorts.join(',')}`
            if (filters != "") apiRoute += `${filters}`
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
    created() {
      var self = this;
      this.gridOptions = {
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
        enableColResize: true,
        onGridReady() {
          var api = this.api;
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
</style>
