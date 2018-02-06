<template>
<div>
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
            // this.gridOptions.api.setRowData(json.result);
            var dataSource = {
              rowCount: null, // behave as infinite scroll
              getRows: function(params) {
                  console.log(params);
                  console.log('asking for ' + params.startRow + ' to ' + params.endRow);
                  fetch(`/api/tasks?start=${params.startRow}&end=${params.endRow}`).then((response) => {
                    return response.json()
                  })
                  .then((json) => {
                    params.successCallback(json.result);
                  });
                  
                  // At this point in your code, you would call the server, using $http if in AngularJS 1.x.
                  // To make the demo look real, wait for 500ms before returning
                  // setTimeout(function() {
                  //     // take a slice of the total rows
                  //     var dataAfterSortingAndFiltering = sortAndFilter(data, params.sortModel, params.filterModel);
                  //     var rowsThisPage = dataAfterSortingAndFiltering.slice(params.startRow, params.endRow);
                  //     // if on or after the last page, work out the last row.
                  //     var lastRow = -1;
                  //     if (dataAfterSortingAndFiltering.length <= params.endRow) {
                  //         lastRow = dataAfterSortingAndFiltering.length;
                  //     }
                  //     // call the success callback
                  //     params.successCallback(rowsThisPage, lastRow);
                  // }, 500);
              }
            };

            this.gridOptions.api.setDatasource(dataSource);
          });
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
          {headerName: "Args", field: "args", cellRenderer: toText},
          {headerName: "Kwargs", field: "kwargs", cellRenderer: toText},
          {headerName: "Status", field: "status", width: 150, suppressSizeToFit: true, cellRendererFramework: StatusChipComponent},
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
      }
    },
    created() {
      var self = this;
      this.gridOptions = {
        debug: true,
        // enableServerSideSorting: true,
        // enableServerSideFilter: true,
        enableColResize: true,
        rowDeselection: true,
        rowModelType: 'infinite',
        cacheOverflowSize: 2,
        maxConcurrentDatasourceRequests: 2,
        infiniteInitialRowCount: 0,
        maxBlocksInCache: 100,
        pagination: true,
        paginationAutoPageSize: true,
        cacheBlockSize: 5,
        suppressCellClickSelection: true,
        enableColResize: true,
        onGridReady() {
          var api = this.api;
          api.setDatasource({
            rowCount: null, // behave as infinite scroll 
            getRows: function(params) {
              console.log(params);
              console.log('asking for ' + params.startRow + ' to ' + params.endRow);
              fetch(`/api/tasks?start=${params.startRow}&end=${params.endRow}`).then((response) => {
                return response.json()
              })
              .then((json) => {
                params.successCallback(json.result, json.count);
                Vue.nextTick(() => {
                  api.sizeColumnsToFit();
                });
              });
            }
          });
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
</style>
