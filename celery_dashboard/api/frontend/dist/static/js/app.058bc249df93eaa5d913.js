webpackJsonp([1],{

/***/ 244:
/***/ (function(module, exports) {

// removed by extract-text-webpack-plugin

/***/ }),

/***/ 245:
/***/ (function(module, exports) {

// removed by extract-text-webpack-plugin

/***/ }),

/***/ 246:
/***/ (function(module, exports) {

// removed by extract-text-webpack-plugin

/***/ }),

/***/ 247:
/***/ (function(module, exports, __webpack_require__) {


/* styles */
__webpack_require__(296)

var Component = __webpack_require__(21)(
  /* script */
  __webpack_require__(288),
  /* template */
  __webpack_require__(315),
  /* scopeId */
  "data-v-d4bb9afe",
  /* cssModules */
  null
)

module.exports = Component.exports


/***/ }),

/***/ 248:
/***/ (function(module, exports, __webpack_require__) {


/* styles */
__webpack_require__(295)

var Component = __webpack_require__(21)(
  /* script */
  __webpack_require__(289),
  /* template */
  __webpack_require__(313),
  /* scopeId */
  "data-v-4706de26",
  /* cssModules */
  null
)

module.exports = Component.exports


/***/ }),

/***/ 249:
/***/ (function(module, exports, __webpack_require__) {


/* styles */
__webpack_require__(292)

var Component = __webpack_require__(21)(
  /* script */
  __webpack_require__(290),
  /* template */
  __webpack_require__(308),
  /* scopeId */
  "data-v-1d447d4c",
  /* cssModules */
  null
)

module.exports = Component.exports


/***/ }),

/***/ 281:
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
Object.defineProperty(__webpack_exports__, "__esModule", { value: true });
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0__SideMenu__ = __webpack_require__(302);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0__SideMenu___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_0__SideMenu__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1__Snackbar__ = __webpack_require__(303);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1__Snackbar___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_1__Snackbar__);
//
//
//
//
//
//
//
//




/* harmony default export */ __webpack_exports__["default"] = ({
    name: 'app-layout',
    components: {
        SideMenu: __WEBPACK_IMPORTED_MODULE_0__SideMenu___default.a, Snackbar: __WEBPACK_IMPORTED_MODULE_1__Snackbar___default.a
    }
});

/***/ }),

/***/ 282:
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
Object.defineProperty(__webpack_exports__, "__esModule", { value: true });
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_ag_grid_vue__ = __webpack_require__(63);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_ag_grid_vue___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_0_ag_grid_vue__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1__utils_bus_js__ = __webpack_require__(37);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2_vue__ = __webpack_require__(23);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_3_jquery__ = __webpack_require__(90);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_3_jquery___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_3_jquery__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_4_jquery_sparkline__ = __webpack_require__(124);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_4_jquery_sparkline___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_4_jquery_sparkline__);
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//







/* harmony default export */ __webpack_exports__["default"] = ({
  name: "queues-grid",
  data() {
    return {
      gridOptions: null,
      loading: false,
      runningPoller: null,
      dataByQueue: {},
      refreshInterval: 5
    };
  },
  components: {
    AgGridVue: __WEBPACK_IMPORTED_MODULE_0_ag_grid_vue__["AgGridVue"]
  },
  methods: {
    createColDefs() {
      return [{ headerName: "Queue", field: "routing_key" }, { headerName: "Started", field: "STARTED" }, { headerName: "Queued", field: "QUEUED" }, { headerName: "Waiting for retry", field: "RETRY" }, {
        headerName: "Progress", field: "progress", cellRenderer(params) {
          if (!!params.data) {
            return `<span id="chart-${params.data.routing_key}"></span>`;
          }
        }, cellClass: 'with-graph'
      }];
    },
    poller() {
      if (this.loading) return;
      this.loading = true;
      fetch("/api/queues").then(response => {
        this.loading = false;
        if (response.status !== 200) return __WEBPACK_IMPORTED_MODULE_1__utils_bus_js__["a" /* EventBus */].$emit('snackbar:show', {
          text: "An error occurred",
          color: "error",
          timeout: 2000
        });
        return response.json();
      }).then(json => {
        json.result.forEach(record => {
          let queue = record.routing_key;
          let oldProgress = (this.dataByQueue[queue] || {}).progress || [];
          oldProgress.unshift(record.ALL);
          oldProgress = oldProgress.slice(0, 200);
          this.dataByQueue[queue] = {
            routing_key: queue,
            running_jobs: (json[queue] || []).length,
            progress: oldProgress
          };
        });
        if (this.gridOptions.api) {
          this.gridOptions.api.setRowData(json.result);
          __WEBPACK_IMPORTED_MODULE_2_vue__["default"].nextTick(() => {
            this.gridOptions.api.sizeColumnsToFit();
            Object.keys(this.dataByQueue).forEach(queue => {
              __WEBPACK_IMPORTED_MODULE_3_jquery__(`#chart-${queue}`).sparkline(this.dataByQueue[queue].progress, {
                defaultPixelsPerValue: 1,
                height: 100
              });
            });
          });
        }
      });
    },
    setPoller() {
      this.poller();
      this.runningPoller = setInterval(this.poller, this.refreshInterval * 1000);
    },
    handlePoller(poll) {
      if (poll) {
        this.setPoller();
      } else {
        clearInterval(this.runningPoller);
      }
    }
  },
  created() {
    this.setPoller();
    __WEBPACK_IMPORTED_MODULE_1__utils_bus_js__["a" /* EventBus */].$on('queuespolling', this.handlePoller);
    this.gridOptions = {
      enableColResize: true,
      rowDeselection: true,
      suppressCellClickSelection: true,
      rowHeight: 120,
      deltaRowDataMode: true,
      getRowNodeId(data) {
        return data.routing_key;
      },
      columnDefs: this.createColDefs()
    };
    __WEBPACK_IMPORTED_MODULE_2_vue__["default"].nextTick(() => {
      this.gridOptions.api.sizeColumnsToFit();
    });
  },
  watch: {
    refreshInterval: function () {
      clearInterval(this.runningPoller);
      this.setPoller();
    }
  }
});

/***/ }),

/***/ 283:
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
Object.defineProperty(__webpack_exports__, "__esModule", { value: true });
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//

/* harmony default export */ __webpack_exports__["default"] = ({
    name: "side-menu",
    data() {
        return {
            drawer: false
        };
    }
});

/***/ }),

/***/ 284:
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
Object.defineProperty(__webpack_exports__, "__esModule", { value: true });
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0__utils_bus_js__ = __webpack_require__(37);
//
//
//
//
//
//
//
//
//
//
//



/* harmony default export */ __webpack_exports__["default"] = ({
    name: 'snackbar',
    data() {
        return {
            timeout: null,
            color: null,
            open: false,
            text: null
        };
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
        __WEBPACK_IMPORTED_MODULE_0__utils_bus_js__["a" /* EventBus */].$on('snackbar:show', this.showSnackbar);
    }
});

/***/ }),

/***/ 285:
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
Object.defineProperty(__webpack_exports__, "__esModule", { value: true });
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_vue__ = __webpack_require__(23);
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//



/* harmony default export */ __webpack_exports__["default"] = ({
  name: "task-dialog",
  props: ["openDialog", "task"],
  data() {
    return {
      open: false
    };
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
  methods: {}
});

/***/ }),

/***/ 286:
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
Object.defineProperty(__webpack_exports__, "__esModule", { value: true });
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_vue__ = __webpack_require__(23);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_ag_grid_vue__ = __webpack_require__(63);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_ag_grid_vue___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_1_ag_grid_vue__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2_whatwg_fetch__ = __webpack_require__(93);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2_whatwg_fetch___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_2_whatwg_fetch__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_3_vuetify__ = __webpack_require__(94);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_3_vuetify___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_3_vuetify__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_4__TaskDialog__ = __webpack_require__(304);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_4__TaskDialog___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_4__TaskDialog__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_5__utils_bus_js__ = __webpack_require__(37);
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//









const moment = __webpack_require__(0);

const StatusChipComponent = __WEBPACK_IMPORTED_MODULE_0_vue__["default"].extend({
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
      let color = "primary";
      if (this.params.value == "QUEUED") color = "orange";
      if (this.params.value == "SUCCESS") color = "green";
      if (this.params.value == "FAILURE") color = "red";
      if (this.params.value == "RETRY") color = "indigo";
      return color;
    },
    revoke() {
      fetch(`/api/task/${this.params.data.task_id}/revoke`).then(response => {
        if (response.status !== 200) return __WEBPACK_IMPORTED_MODULE_5__utils_bus_js__["a" /* EventBus */].$emit('snackbar:show', { text: "An error occurred", color: "error", timeout: 2000 });
        return __WEBPACK_IMPORTED_MODULE_5__utils_bus_js__["a" /* EventBus */].$emit('snackbar:show', { text: "Task successfully cancelled", color: "success", timeout: 2000 });
      });
    },
    requeue() {
      fetch(`/api/task/${this.params.data.task_id}/requeue`).then(response => {
        if (response.status !== 200) return __WEBPACK_IMPORTED_MODULE_5__utils_bus_js__["a" /* EventBus */].$emit('snackbar:show', { text: "An error occurred", color: "error", timeout: 2000 });
        return __WEBPACK_IMPORTED_MODULE_5__utils_bus_js__["a" /* EventBus */].$emit('snackbar:show', { text: "Task successfully queued", color: "success", timeout: 2000 });
      });
    }
  }
});

const DateCellComponent = __WEBPACK_IMPORTED_MODULE_0_vue__["default"].extend({
  template: `
            <div>
              <pre class="simple-text">{{ getDateText() }}</pre>
              <v-tooltip right v-if="(params.data.meta || {}).progress">
                <v-progress-circular :value="params.data.meta.progress" :rotate="-90" color="lime" slot="activator"></v-progress-circular>
                <span>Completed {{ params.data.meta.progress }}%</span>
              </v-tooltip>
            </div>
            `,
  methods: {
    getDateText() {
      let s = [];
      if (this.params.value !== undefined) {
        if (this.params.data.date_done) s.push("Done: " + moment.utc(this.params.data.date_done).fromNow());
        if (this.params.data.date_queued) s.push("Queued: " + moment.utc(this.params.data.date_queued).fromNow());
        if (this.params.data.eta) s.push("Eta: " + moment.utc(this.params.data.eta).fromNow());
      }
      return s.join("\n");
    }
  }
});

/* harmony default export */ __webpack_exports__["default"] = ({
  name: 'tasks-grid',
  data() {
    return {
      gridOptions: null,
      openDialog: false,
      taskToOpen: {},
      filters: {
        task: this.$route.query.task,
        status: this.$route.query.status,
        taskId: this.$route.query.taskId,
        queue: this.$route.query.queue,
        exception: this.$route.query.exception
      }
    };
  },
  components: {
    AgGridVue: __WEBPACK_IMPORTED_MODULE_1_ag_grid_vue__["AgGridVue"],
    TaskDialog: __WEBPACK_IMPORTED_MODULE_4__TaskDialog___default.a
  },
  methods: {
    cancelAll() {
      let filters = {};
      let self = this;
      Object.keys(this.filters).forEach(filter => {
        let val = this.filters[filter];
        if (!!val && (filter !== "status" || val !== "ALL")) filters[filter] = val;
      });
      fetch('/api/tasks', {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(filters)
      }).then(response => {
        if (response.status !== 200) return __WEBPACK_IMPORTED_MODULE_5__utils_bus_js__["a" /* EventBus */].$emit('snackbar:show', { text: "An error occurred", color: "error", timeout: 2000 });
        return response.json();
      }).then(json => {
        return __WEBPACK_IMPORTED_MODULE_5__utils_bus_js__["a" /* EventBus */].$emit('snackbar:show', { text: `${json.count} task(s) successfully cancelled`, color: "success", timeout: 2000 });
      });
    },
    requeueAll() {
      let filters = {};
      let self = this;
      Object.keys(this.filters).forEach(filter => {
        let val = this.filters[filter];
        if (!!val && (filter !== "status" || val !== "ALL")) filters[filter] = val;
      });
      fetch('/api/tasks', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(filters)
      }).then(response => {
        if (response.status !== 200) return __WEBPACK_IMPORTED_MODULE_5__utils_bus_js__["a" /* EventBus */].$emit('snackbar:show', { text: "An error occurred", color: "error", timeout: 2000 });
        return response.json();
      }).then(json => {
        return __WEBPACK_IMPORTED_MODULE_5__utils_bus_js__["a" /* EventBus */].$emit('snackbar:show', { text: `${json.count} task(s) successfully requeued`, color: "success", timeout: 2000 });
      });
    },
    filterData() {
      this.$router.push({ path: "jobs", query: this.filters });
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
      return [{ headerName: "Task", field: "name", width: 200, suppressSizeToFit: true }, { headerName: "Queue", field: "routing_key", width: 150, suppressSizeToFit: true }, { headerName: "Args", field: "args", cellRenderer: toText, suppressSorting: true }, { headerName: "Kwargs", field: "kwargs", cellRenderer: toText, suppressSorting: true }, { headerName: "Status", field: "status", width: 150, suppressSizeToFit: true, cellRendererFramework: StatusChipComponent, cellClass: ['centered-cell'] }, {
        headerName: "Date", field: "date_done", width: 180, cellRendererFramework: DateCellComponent
      }];
    },
    getFiltersParams() {
      let filtersArr = [];
      Object.keys(this.filters).forEach(param => {
        let val = this.filters[param];
        if (!!val && (param !== "status" || val !== "ALL")) filtersArr.push(`${param}=${val}`);
      });
      return filtersArr;
    },
    getDatasource(api) {
      let self = this;
      api.showLoadingOverlay();
      return {
        rowCount: null, // behave as infinite scroll
        getRows(params) {
          let sorts = [];
          params.sortModel.forEach(model => {
            sorts.push(`${model.colId}:${model.sort}`);
          });
          let filters = self.getFiltersParams();
          let apiRoute = `/api/tasks?start=${params.startRow}&end=${params.endRow}&sort=${sorts.join(',')}`;
          if (filters != "") apiRoute += `&${filters.join("&")}`;
          fetch(apiRoute).then(response => {
            api.hideOverlay();
            return response.json();
          }).then(json => {
            params.successCallback(json.result, json.count);
            __WEBPACK_IMPORTED_MODULE_0_vue__["default"].nextTick(() => {
              api.sizeColumnsToFit();
            });
          });
        }
      };
    }
  },
  beforeMount() {
    let self = this;
    this.gridOptions = {
      context: {
        componentParent: self
      },
      overlayLoadingTemplate: '<span class="ag-overlay-loading-center">Loading jobs...</span>',
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
    __WEBPACK_IMPORTED_MODULE_0_vue__["default"].nextTick(() => {
      this.gridOptions.api.sizeColumnsToFit();
    });
  }
});

/***/ }),

/***/ 287:
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
Object.defineProperty(__webpack_exports__, "__esModule", { value: true });
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_ag_grid_vue__ = __webpack_require__(63);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_ag_grid_vue___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_0_ag_grid_vue__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1__utils_bus_js__ = __webpack_require__(37);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2_vue__ = __webpack_require__(23);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_3_jquery__ = __webpack_require__(90);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_3_jquery___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_3_jquery__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_4_jquery_sparkline__ = __webpack_require__(124);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_4_jquery_sparkline___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_4_jquery_sparkline__);
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//







/* harmony default export */ __webpack_exports__["default"] = ({
  name: "workers-grid",
  data() {
    return {
      gridOptions: null,
      loading: false,
      runningPoller: null,
      refreshInterval: 5
    };
  },
  components: {
    AgGridVue: __WEBPACK_IMPORTED_MODULE_0_ag_grid_vue__["AgGridVue"]
  },
  methods: {
    createColDefs() {
      return [{ headerName: "Worker", field: "name" }, { headerName: "Broker", field: "broker" }, { headerName: "Pool size", field: "poolSize" }, {
        headerName: "Tasks", field: "tasks", cellRenderer(params) {
          if (!!params.data) {
            return `<span id="chart-worker-${params.data.pid}"></span>`;
          }
        }, cellClass: 'with-graph'
      }];
    },
    poller() {
      if (this.loading) return;
      this.loading = true;
      fetch("/api/workers").then(response => {
        this.loading = false;
        if (response.status !== 200) return __WEBPACK_IMPORTED_MODULE_1__utils_bus_js__["a" /* EventBus */].$emit('snackbar:show', {
          text: "An error occurred",
          color: "error",
          timeout: 2000
        });
        return response.json();
      }).then(json => {
        if (this.gridOptions.api) {
          this.gridOptions.api.setRowData(json.result);
          __WEBPACK_IMPORTED_MODULE_2_vue__["default"].nextTick(() => {
            this.gridOptions.api.sizeColumnsToFit();
            json.result.forEach(worker => {
              let taskCounts = [];
              let taskMappings = {};
              let count = 0;
              Object.keys(worker.tasks).forEach(taskName => {
                taskMappings[count] = taskName;
                taskCounts.push(worker.tasks[taskName]);
                count += 1;
              });
              __WEBPACK_IMPORTED_MODULE_3_jquery__(`#chart-worker-${worker.pid}`).sparkline(taskCounts, {
                type: 'bar',
                height: 100,
                barWidth: 10,
                tooltipFormat: '{{offset:offset}} ({{value}})',
                tooltipValueLookups: {
                  'offset': taskMappings
                }
              });
            });
          });
        }
      });
    },
    setPoller() {
      this.poller();
      this.runningPoller = setInterval(this.poller, this.refreshInterval * 1000);
    },
    handlePoller(poll) {
      if (poll) {
        this.setPoller();
      } else {
        clearInterval(this.runningPoller);
      }
    }
  },
  created() {
    this.setPoller();
    __WEBPACK_IMPORTED_MODULE_1__utils_bus_js__["a" /* EventBus */].$on('workerspolling', this.handlePoller);
    this.gridOptions = {
      enableColResize: true,
      rowDeselection: true,
      suppressCellClickSelection: true,
      rowHeight: 120,
      deltaRowDataMode: true,
      getRowNodeId(data) {
        return data.pid;
      },
      columnDefs: this.createColDefs()
    };
    __WEBPACK_IMPORTED_MODULE_2_vue__["default"].nextTick(() => {
      this.gridOptions.api.sizeColumnsToFit();
    });
  },
  watch: {
    refreshInterval: function () {
      clearInterval(this.runningPoller);
      this.setPoller();
    }
  }
});

/***/ }),

/***/ 288:
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
Object.defineProperty(__webpack_exports__, "__esModule", { value: true });
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0__components_TasksGrid__ = __webpack_require__(305);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0__components_TasksGrid___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_0__components_TasksGrid__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1__components_AppLayout__ = __webpack_require__(91);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1__components_AppLayout___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_1__components_AppLayout__);
//
//
//
//
//
//




/* harmony default export */ __webpack_exports__["default"] = ({
  name: 'jobs',
  data() {
    return {};
  },
  components: {
    TasksGrid: __WEBPACK_IMPORTED_MODULE_0__components_TasksGrid___default.a,
    AppLayout: __WEBPACK_IMPORTED_MODULE_1__components_AppLayout___default.a
  },
  methods: {}
});

/***/ }),

/***/ 289:
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
Object.defineProperty(__webpack_exports__, "__esModule", { value: true });
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0__components_AppLayout__ = __webpack_require__(91);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0__components_AppLayout___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_0__components_AppLayout__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1__components_QueuesGrid__ = __webpack_require__(301);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1__components_QueuesGrid___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_1__components_QueuesGrid__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2__utils_bus_js__ = __webpack_require__(37);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_3_whatwg_fetch__ = __webpack_require__(93);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_3_whatwg_fetch___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_3_whatwg_fetch__);
//
//
//
//
//
//






/* harmony default export */ __webpack_exports__["default"] = ({
  name: 'queues',
  data() {
    return {
      runningPoller: null
    };
  },
  components: {
    AppLayout: __WEBPACK_IMPORTED_MODULE_0__components_AppLayout___default.a, QueuesGrid: __WEBPACK_IMPORTED_MODULE_1__components_QueuesGrid___default.a
  },
  methods: {},
  beforeRouteLeave(to, from, next) {
    __WEBPACK_IMPORTED_MODULE_2__utils_bus_js__["a" /* EventBus */].$emit("queuespolling", false);
    next();
  },
  beforeRouteEnter(to, from, next) {
    __WEBPACK_IMPORTED_MODULE_2__utils_bus_js__["a" /* EventBus */].$emit("queuespolling", true);
    next();
  }
});

/***/ }),

/***/ 290:
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
Object.defineProperty(__webpack_exports__, "__esModule", { value: true });
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0__components_AppLayout__ = __webpack_require__(91);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0__components_AppLayout___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_0__components_AppLayout__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1__components_WorkersGrid__ = __webpack_require__(306);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1__components_WorkersGrid___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_1__components_WorkersGrid__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2__utils_bus_js__ = __webpack_require__(37);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_3_whatwg_fetch__ = __webpack_require__(93);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_3_whatwg_fetch___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_3_whatwg_fetch__);
//
//
//
//
//
//






/* harmony default export */ __webpack_exports__["default"] = ({
  name: 'workers',
  data() {
    return {
      runningPoller: null
    };
  },
  components: {
    AppLayout: __WEBPACK_IMPORTED_MODULE_0__components_AppLayout___default.a, WorkersGrid: __WEBPACK_IMPORTED_MODULE_1__components_WorkersGrid___default.a
  },
  methods: {},
  beforeRouteLeave(to, from, next) {
    __WEBPACK_IMPORTED_MODULE_2__utils_bus_js__["a" /* EventBus */].$emit("workerspolling", false);
    next();
  },
  beforeRouteEnter(to, from, next) {
    __WEBPACK_IMPORTED_MODULE_2__utils_bus_js__["a" /* EventBus */].$emit("workerspolling", true);
    next();
  }
});

/***/ }),

/***/ 291:
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
Object.defineProperty(__webpack_exports__, "__esModule", { value: true });
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_vue__ = __webpack_require__(23);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_vuetify__ = __webpack_require__(94);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_vuetify___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_1_vuetify__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2__routes_Jobs__ = __webpack_require__(247);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2__routes_Jobs___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_2__routes_Jobs__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_3__routes_Queues__ = __webpack_require__(248);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_3__routes_Queues___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_3__routes_Queues__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_4__routes_Workers__ = __webpack_require__(249);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_4__routes_Workers___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_4__routes_Workers__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_5_vue_router__ = __webpack_require__(250);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_6__node_modules_ag_grid_dist_styles_ag_grid_css__ = __webpack_require__(244);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_6__node_modules_ag_grid_dist_styles_ag_grid_css___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_6__node_modules_ag_grid_dist_styles_ag_grid_css__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_7__node_modules_ag_grid_dist_styles_ag_theme_material_css__ = __webpack_require__(245);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_7__node_modules_ag_grid_dist_styles_ag_theme_material_css___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_7__node_modules_ag_grid_dist_styles_ag_theme_material_css__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_8__node_modules_vuetify_dist_vuetify_min_css__ = __webpack_require__(246);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_8__node_modules_vuetify_dist_vuetify_min_css___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_8__node_modules_vuetify_dist_vuetify_min_css__);
// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.











__WEBPACK_IMPORTED_MODULE_0_vue__["default"].config.productionTip = false;
__WEBPACK_IMPORTED_MODULE_0_vue__["default"].use(__WEBPACK_IMPORTED_MODULE_1_vuetify___default.a);
__WEBPACK_IMPORTED_MODULE_0_vue__["default"].use(__WEBPACK_IMPORTED_MODULE_5_vue_router__["a" /* default */]);

const routes = [{ path: '/jobs', name: 'jobs', component: __WEBPACK_IMPORTED_MODULE_2__routes_Jobs___default.a }, { path: '/queues', name: 'queues', component: __WEBPACK_IMPORTED_MODULE_3__routes_Queues___default.a }, { path: '/workers', name: 'workers', component: __WEBPACK_IMPORTED_MODULE_4__routes_Workers___default.a }, { path: '*', redirect: '/workers' }];

const router = new __WEBPACK_IMPORTED_MODULE_5_vue_router__["a" /* default */]({
    routes
});

/* eslint-disable no-new */
new __WEBPACK_IMPORTED_MODULE_0_vue__["default"]({
    router
}).$mount('#app');

/***/ }),

/***/ 292:
/***/ (function(module, exports) {

// removed by extract-text-webpack-plugin

/***/ }),

/***/ 293:
/***/ (function(module, exports) {

// removed by extract-text-webpack-plugin

/***/ }),

/***/ 294:
/***/ (function(module, exports) {

// removed by extract-text-webpack-plugin

/***/ }),

/***/ 295:
/***/ (function(module, exports) {

// removed by extract-text-webpack-plugin

/***/ }),

/***/ 296:
/***/ (function(module, exports) {

// removed by extract-text-webpack-plugin

/***/ }),

/***/ 297:
/***/ (function(module, exports, __webpack_require__) {

var map = {
	"./af": 125,
	"./af.js": 125,
	"./ar": 132,
	"./ar-dz": 126,
	"./ar-dz.js": 126,
	"./ar-kw": 127,
	"./ar-kw.js": 127,
	"./ar-ly": 128,
	"./ar-ly.js": 128,
	"./ar-ma": 129,
	"./ar-ma.js": 129,
	"./ar-sa": 130,
	"./ar-sa.js": 130,
	"./ar-tn": 131,
	"./ar-tn.js": 131,
	"./ar.js": 132,
	"./az": 133,
	"./az.js": 133,
	"./be": 134,
	"./be.js": 134,
	"./bg": 135,
	"./bg.js": 135,
	"./bm": 136,
	"./bm.js": 136,
	"./bn": 137,
	"./bn.js": 137,
	"./bo": 138,
	"./bo.js": 138,
	"./br": 139,
	"./br.js": 139,
	"./bs": 140,
	"./bs.js": 140,
	"./ca": 141,
	"./ca.js": 141,
	"./cs": 142,
	"./cs.js": 142,
	"./cv": 143,
	"./cv.js": 143,
	"./cy": 144,
	"./cy.js": 144,
	"./da": 145,
	"./da.js": 145,
	"./de": 148,
	"./de-at": 146,
	"./de-at.js": 146,
	"./de-ch": 147,
	"./de-ch.js": 147,
	"./de.js": 148,
	"./dv": 149,
	"./dv.js": 149,
	"./el": 150,
	"./el.js": 150,
	"./en-au": 151,
	"./en-au.js": 151,
	"./en-ca": 152,
	"./en-ca.js": 152,
	"./en-gb": 153,
	"./en-gb.js": 153,
	"./en-ie": 154,
	"./en-ie.js": 154,
	"./en-nz": 155,
	"./en-nz.js": 155,
	"./eo": 156,
	"./eo.js": 156,
	"./es": 159,
	"./es-do": 157,
	"./es-do.js": 157,
	"./es-us": 158,
	"./es-us.js": 158,
	"./es.js": 159,
	"./et": 160,
	"./et.js": 160,
	"./eu": 161,
	"./eu.js": 161,
	"./fa": 162,
	"./fa.js": 162,
	"./fi": 163,
	"./fi.js": 163,
	"./fo": 164,
	"./fo.js": 164,
	"./fr": 167,
	"./fr-ca": 165,
	"./fr-ca.js": 165,
	"./fr-ch": 166,
	"./fr-ch.js": 166,
	"./fr.js": 167,
	"./fy": 168,
	"./fy.js": 168,
	"./gd": 169,
	"./gd.js": 169,
	"./gl": 170,
	"./gl.js": 170,
	"./gom-latn": 171,
	"./gom-latn.js": 171,
	"./gu": 172,
	"./gu.js": 172,
	"./he": 173,
	"./he.js": 173,
	"./hi": 174,
	"./hi.js": 174,
	"./hr": 175,
	"./hr.js": 175,
	"./hu": 176,
	"./hu.js": 176,
	"./hy-am": 177,
	"./hy-am.js": 177,
	"./id": 178,
	"./id.js": 178,
	"./is": 179,
	"./is.js": 179,
	"./it": 180,
	"./it.js": 180,
	"./ja": 181,
	"./ja.js": 181,
	"./jv": 182,
	"./jv.js": 182,
	"./ka": 183,
	"./ka.js": 183,
	"./kk": 184,
	"./kk.js": 184,
	"./km": 185,
	"./km.js": 185,
	"./kn": 186,
	"./kn.js": 186,
	"./ko": 187,
	"./ko.js": 187,
	"./ky": 188,
	"./ky.js": 188,
	"./lb": 189,
	"./lb.js": 189,
	"./lo": 190,
	"./lo.js": 190,
	"./lt": 191,
	"./lt.js": 191,
	"./lv": 192,
	"./lv.js": 192,
	"./me": 193,
	"./me.js": 193,
	"./mi": 194,
	"./mi.js": 194,
	"./mk": 195,
	"./mk.js": 195,
	"./ml": 196,
	"./ml.js": 196,
	"./mr": 197,
	"./mr.js": 197,
	"./ms": 199,
	"./ms-my": 198,
	"./ms-my.js": 198,
	"./ms.js": 199,
	"./mt": 200,
	"./mt.js": 200,
	"./my": 201,
	"./my.js": 201,
	"./nb": 202,
	"./nb.js": 202,
	"./ne": 203,
	"./ne.js": 203,
	"./nl": 205,
	"./nl-be": 204,
	"./nl-be.js": 204,
	"./nl.js": 205,
	"./nn": 206,
	"./nn.js": 206,
	"./pa-in": 207,
	"./pa-in.js": 207,
	"./pl": 208,
	"./pl.js": 208,
	"./pt": 210,
	"./pt-br": 209,
	"./pt-br.js": 209,
	"./pt.js": 210,
	"./ro": 211,
	"./ro.js": 211,
	"./ru": 212,
	"./ru.js": 212,
	"./sd": 213,
	"./sd.js": 213,
	"./se": 214,
	"./se.js": 214,
	"./si": 215,
	"./si.js": 215,
	"./sk": 216,
	"./sk.js": 216,
	"./sl": 217,
	"./sl.js": 217,
	"./sq": 218,
	"./sq.js": 218,
	"./sr": 220,
	"./sr-cyrl": 219,
	"./sr-cyrl.js": 219,
	"./sr.js": 220,
	"./ss": 221,
	"./ss.js": 221,
	"./sv": 222,
	"./sv.js": 222,
	"./sw": 223,
	"./sw.js": 223,
	"./ta": 224,
	"./ta.js": 224,
	"./te": 225,
	"./te.js": 225,
	"./tet": 226,
	"./tet.js": 226,
	"./th": 227,
	"./th.js": 227,
	"./tl-ph": 228,
	"./tl-ph.js": 228,
	"./tlh": 229,
	"./tlh.js": 229,
	"./tr": 230,
	"./tr.js": 230,
	"./tzl": 231,
	"./tzl.js": 231,
	"./tzm": 233,
	"./tzm-latn": 232,
	"./tzm-latn.js": 232,
	"./tzm.js": 233,
	"./uk": 234,
	"./uk.js": 234,
	"./ur": 235,
	"./ur.js": 235,
	"./uz": 237,
	"./uz-latn": 236,
	"./uz-latn.js": 236,
	"./uz.js": 237,
	"./vi": 238,
	"./vi.js": 238,
	"./x-pseudo": 239,
	"./x-pseudo.js": 239,
	"./yo": 240,
	"./yo.js": 240,
	"./zh-cn": 241,
	"./zh-cn.js": 241,
	"./zh-hk": 242,
	"./zh-hk.js": 242,
	"./zh-tw": 243,
	"./zh-tw.js": 243
};
function webpackContext(req) {
	return __webpack_require__(webpackContextResolve(req));
};
function webpackContextResolve(req) {
	var id = map[req];
	if(!(id + 1)) // check for number or string
		throw new Error("Cannot find module '" + req + "'.");
	return id;
};
webpackContext.keys = function webpackContextKeys() {
	return Object.keys(map);
};
webpackContext.resolve = webpackContextResolve;
module.exports = webpackContext;
webpackContext.id = 297;

/***/ }),

/***/ 301:
/***/ (function(module, exports, __webpack_require__) {

var Component = __webpack_require__(21)(
  /* script */
  __webpack_require__(282),
  /* template */
  __webpack_require__(316),
  /* scopeId */
  null,
  /* cssModules */
  null
)

module.exports = Component.exports


/***/ }),

/***/ 302:
/***/ (function(module, exports, __webpack_require__) {

var Component = __webpack_require__(21)(
  /* script */
  __webpack_require__(283),
  /* template */
  __webpack_require__(307),
  /* scopeId */
  null,
  /* cssModules */
  null
)

module.exports = Component.exports


/***/ }),

/***/ 303:
/***/ (function(module, exports, __webpack_require__) {

var Component = __webpack_require__(21)(
  /* script */
  __webpack_require__(284),
  /* template */
  __webpack_require__(314),
  /* scopeId */
  null,
  /* cssModules */
  null
)

module.exports = Component.exports


/***/ }),

/***/ 304:
/***/ (function(module, exports, __webpack_require__) {

var Component = __webpack_require__(21)(
  /* script */
  __webpack_require__(285),
  /* template */
  __webpack_require__(310),
  /* scopeId */
  null,
  /* cssModules */
  null
)

module.exports = Component.exports


/***/ }),

/***/ 305:
/***/ (function(module, exports, __webpack_require__) {


/* styles */
__webpack_require__(293)

var Component = __webpack_require__(21)(
  /* script */
  __webpack_require__(286),
  /* template */
  __webpack_require__(309),
  /* scopeId */
  null,
  /* cssModules */
  null
)

module.exports = Component.exports


/***/ }),

/***/ 306:
/***/ (function(module, exports, __webpack_require__) {

var Component = __webpack_require__(21)(
  /* script */
  __webpack_require__(287),
  /* template */
  __webpack_require__(312),
  /* scopeId */
  null,
  /* cssModules */
  null
)

module.exports = Component.exports


/***/ }),

/***/ 307:
/***/ (function(module, exports) {

module.exports={render:function (){var _vm=this;var _h=_vm.$createElement;var _c=_vm._self._c||_h;
  return _c('div', [_c('v-navigation-drawer', {
    attrs: {
      "temporary": "",
      "absolute": "",
      "light": ""
    },
    model: {
      value: (_vm.drawer),
      callback: function($$v) {
        _vm.drawer = $$v
      },
      expression: "drawer"
    }
  }, [_c('v-toolbar', {
    attrs: {
      "flat": ""
    }
  }, [_c('v-list', [_c('v-list-tile', [_c('v-list-tile-title', {
    staticClass: "title"
  }, [_vm._v("\n                Celery Dashboard\n            ")])], 1)], 1)], 1), _vm._v(" "), _c('v-divider'), _vm._v(" "), _c('v-list', {
    staticClass: "pt-0",
    attrs: {
      "dense": ""
    }
  }, [_c('v-list-tile', {
    attrs: {
      "to": {
        name: 'workers'
      }
    }
  }, [_c('v-list-tile-action', [_c('v-icon', [_vm._v("home")])], 1), _vm._v(" "), _c('v-list-tile-content', [_c('v-list-tile-title', [_vm._v("Workers")])], 1)], 1), _vm._v(" "), _c('v-list-tile', {
    attrs: {
      "to": {
        name: 'jobs'
      }
    }
  }, [_c('v-list-tile-action', [_c('v-icon', [_vm._v("grid_on")])], 1), _vm._v(" "), _c('v-list-tile-content', [_c('v-list-tile-title', [_vm._v("Jobs")])], 1)], 1), _vm._v(" "), _c('v-list-tile', {
    attrs: {
      "to": {
        name: 'queues'
      }
    }
  }, [_c('v-list-tile-action', [_c('v-icon', [_vm._v("compare_arrows")])], 1), _vm._v(" "), _c('v-list-tile-content', [_c('v-list-tile-title', [_vm._v("Queues")])], 1)], 1)], 1)], 1), _vm._v(" "), _c('v-toolbar', {
    attrs: {
      "dark": "",
      "color": "primary"
    }
  }, [_c('v-toolbar-side-icon', {
    on: {
      "click": function($event) {
        $event.stopPropagation();
        _vm.drawer = !_vm.drawer
      }
    }
  }), _vm._v(" "), _c('v-toolbar-title', {
    staticClass: "white--text"
  }, [_vm._v("Celery Dashboard")])], 1)], 1)
},staticRenderFns: []}

/***/ }),

/***/ 308:
/***/ (function(module, exports) {

module.exports={render:function (){var _vm=this;var _h=_vm.$createElement;var _c=_vm._self._c||_h;
  return _c('app-layout', [_c('workers-grid')], 1)
},staticRenderFns: []}

/***/ }),

/***/ 309:
/***/ (function(module, exports) {

module.exports={render:function (){var _vm=this;var _h=_vm.$createElement;var _c=_vm._self._c||_h;
  return _c('div', [_c('div', {
    staticClass: "filter-box"
  }, [_c('v-form', {
    ref: "form"
  }, [_c('v-layout', {
    attrs: {
      "row": "",
      "wrap": ""
    }
  }, [_c('v-text-field', {
    attrs: {
      "label": "Id"
    },
    model: {
      value: (_vm.filters.taskId),
      callback: function($$v) {
        _vm.$set(_vm.filters, "taskId", $$v)
      },
      expression: "filters.taskId"
    }
  }), _vm._v(" "), _c('v-text-field', {
    attrs: {
      "label": "Task"
    },
    model: {
      value: (_vm.filters.task),
      callback: function($$v) {
        _vm.$set(_vm.filters, "task", $$v)
      },
      expression: "filters.task"
    }
  }), _vm._v(" "), _c('v-text-field', {
    attrs: {
      "label": "Queue"
    },
    model: {
      value: (_vm.filters.queue),
      callback: function($$v) {
        _vm.$set(_vm.filters, "queue", $$v)
      },
      expression: "filters.queue"
    }
  }), _vm._v(" "), _c('v-select', {
    attrs: {
      "label": "Status",
      "items": ['ALL', 'QUEUED', 'STARTED', 'RETRY', 'SUCCESS', 'FAILURE']
    },
    model: {
      value: (_vm.filters.status),
      callback: function($$v) {
        _vm.$set(_vm.filters, "status", $$v)
      },
      expression: "filters.status"
    }
  }), _vm._v(" "), _c('v-text-field', {
    attrs: {
      "label": "Exception"
    },
    model: {
      value: (_vm.filters.exception),
      callback: function($$v) {
        _vm.$set(_vm.filters, "exception", $$v)
      },
      expression: "filters.exception"
    }
  }), _vm._v(" "), _c('v-btn', {
    attrs: {
      "color": "success"
    },
    on: {
      "click": function($event) {
        _vm.filterData()
      }
    }
  }, [_c('v-icon', {
    attrs: {
      "left": "",
      "dark": ""
    }
  }, [_vm._v("filter_list")]), _vm._v(" Filter\n        ")], 1), _vm._v(" "), _c('v-menu', {
    attrs: {
      "transition": "slide-y-transition",
      "bottom": ""
    }
  }, [_c('v-btn', {
    staticClass: "purple",
    attrs: {
      "slot": "activator",
      "color": "primary",
      "dark": ""
    },
    slot: "activator"
  }, [_c('v-icon', {
    attrs: {
      "left": "",
      "dark": ""
    }
  }, [_vm._v("touch_app")]), _vm._v(" Action\n          ")], 1), _vm._v(" "), _c('v-list', [_c('v-list-tile', {
    on: {
      "click": function($event) {
        _vm.cancelAll()
      }
    }
  }, [_c('v-list-tile-title', [_c('v-icon', {
    attrs: {
      "left": "",
      "dark": "",
      "color": "error"
    }
  }, [_vm._v("delete_forever")]), _vm._v(" Cancel these jobs\n              ")], 1)], 1), _vm._v(" "), _c('v-list-tile', {
    on: {
      "click": function($event) {
        _vm.requeueAll()
      }
    }
  }, [_c('v-list-tile-title', [_c('v-icon', {
    attrs: {
      "left": "",
      "dark": "",
      "color": "success"
    }
  }, [_vm._v("replay")]), _vm._v(" Requeue these jobs\n              ")], 1)], 1)], 1)], 1)], 1)], 1)], 1), _vm._v(" "), _c('task-dialog', {
    attrs: {
      "open-dialog": _vm.openDialog,
      "task": _vm.taskToOpen
    },
    on: {
      "taskdialogclosed": _vm.taskDialogClosed
    }
  }), _vm._v(" "), _c('ag-grid-vue', {
    staticClass: "ag-theme-material grid",
    attrs: {
      "gridOptions": _vm.gridOptions
    }
  })], 1)
},staticRenderFns: []}

/***/ }),

/***/ 310:
/***/ (function(module, exports) {

module.exports={render:function (){var _vm=this;var _h=_vm.$createElement;var _c=_vm._self._c||_h;
  return _c('div', [_c('v-layout', {
    attrs: {
      "row": "",
      "justify-center": ""
    }
  }, [_c('v-dialog', {
    attrs: {
      "scrollable": ""
    },
    model: {
      value: (_vm.open),
      callback: function($$v) {
        _vm.open = $$v
      },
      expression: "open"
    }
  }, [_c('v-card', [_c('v-toolbar', {
    attrs: {
      "color": "primary",
      "dark": ""
    }
  }, [_c('v-toolbar-title', [_vm._v("Task " + _vm._s(_vm.task.task_id))]), _vm._v(" "), _c('v-spacer')], 1), _vm._v(" "), _c('v-card-text', [(_vm.task.status == 'SUCCESS') ? _c('pre', {
    staticClass: "json-formatted"
  }, [_vm._v(_vm._s(_vm.task.result))]) : _c('pre', {
    staticClass: "json-formatted"
  }, [_vm._v(_vm._s(_vm.task.traceback))])])], 1)], 1)], 1)], 1)
},staticRenderFns: []}

/***/ }),

/***/ 311:
/***/ (function(module, exports) {

module.exports={render:function (){var _vm=this;var _h=_vm.$createElement;var _c=_vm._self._c||_h;
  return _c('div', [_c('snackbar'), _vm._v(" "), _c('side-menu'), _vm._v(" "), _vm._t("default")], 2)
},staticRenderFns: []}

/***/ }),

/***/ 312:
/***/ (function(module, exports) {

module.exports={render:function (){var _vm=this;var _h=_vm.$createElement;var _c=_vm._self._c||_h;
  return _c('div', [_c('div', {
    staticClass: "filter-box"
  }, [_c('v-form', {
    ref: "form"
  }, [_c('v-layout', {
    attrs: {
      "row": "",
      "wrap": ""
    }
  }, [_c('v-select', {
    attrs: {
      "label": "Refresh interval",
      "items": [{
        text: '5 seconds',
        value: 5
      }, {
        text: '30 second',
        value: 30
      }, {
        text: '1 minute',
        value: 60
      }, {
        text: '5 minutes',
        value: 300
      }]
    },
    model: {
      value: (_vm.refreshInterval),
      callback: function($$v) {
        _vm.refreshInterval = $$v
      },
      expression: "refreshInterval"
    }
  })], 1)], 1)], 1), _vm._v(" "), _c('ag-grid-vue', {
    staticClass: "ag-theme-material grid",
    attrs: {
      "gridOptions": _vm.gridOptions
    }
  })], 1)
},staticRenderFns: []}

/***/ }),

/***/ 313:
/***/ (function(module, exports) {

module.exports={render:function (){var _vm=this;var _h=_vm.$createElement;var _c=_vm._self._c||_h;
  return _c('app-layout', [_c('queues-grid')], 1)
},staticRenderFns: []}

/***/ }),

/***/ 314:
/***/ (function(module, exports) {

module.exports={render:function (){var _vm=this;var _h=_vm.$createElement;var _c=_vm._self._c||_h;
  return _c('v-snackbar', {
    attrs: {
      "timeout": _vm.timeout,
      "color": _vm.color
    },
    model: {
      value: (_vm.open),
      callback: function($$v) {
        _vm.open = $$v
      },
      expression: "open"
    }
  }, [_vm._v("\n  " + _vm._s(_vm.text) + "\n  "), _c('v-btn', {
    attrs: {
      "dark": "",
      "flat": ""
    },
    nativeOn: {
      "click": function($event) {
        _vm.open = false
      }
    }
  }, [_vm._v("Close")])], 1)
},staticRenderFns: []}

/***/ }),

/***/ 315:
/***/ (function(module, exports) {

module.exports={render:function (){var _vm=this;var _h=_vm.$createElement;var _c=_vm._self._c||_h;
  return _c('app-layout', [_c('tasks-grid')], 1)
},staticRenderFns: []}

/***/ }),

/***/ 316:
/***/ (function(module, exports) {

module.exports={render:function (){var _vm=this;var _h=_vm.$createElement;var _c=_vm._self._c||_h;
  return _c('div', [_c('div', {
    staticClass: "filter-box"
  }, [_c('v-form', {
    ref: "form"
  }, [_c('v-layout', {
    attrs: {
      "row": "",
      "wrap": ""
    }
  }, [_c('v-select', {
    attrs: {
      "label": "Refresh interval",
      "items": [{
        text: '5 seconds',
        value: 5
      }, {
        text: '30 second',
        value: 30
      }, {
        text: '1 minute',
        value: 60
      }, {
        text: '5 minutes',
        value: 300
      }]
    },
    model: {
      value: (_vm.refreshInterval),
      callback: function($$v) {
        _vm.refreshInterval = $$v
      },
      expression: "refreshInterval"
    }
  })], 1)], 1)], 1), _vm._v(" "), _c('ag-grid-vue', {
    staticClass: "ag-theme-material grid",
    attrs: {
      "gridOptions": _vm.gridOptions
    }
  })], 1)
},staticRenderFns: []}

/***/ }),

/***/ 37:
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_vue__ = __webpack_require__(23);


const EventBus = new __WEBPACK_IMPORTED_MODULE_0_vue__["default"]();
/* harmony export (immutable) */ __webpack_exports__["a"] = EventBus;


/***/ }),

/***/ 91:
/***/ (function(module, exports, __webpack_require__) {


/* styles */
__webpack_require__(294)

var Component = __webpack_require__(21)(
  /* script */
  __webpack_require__(281),
  /* template */
  __webpack_require__(311),
  /* scopeId */
  null,
  /* cssModules */
  null
)

module.exports = Component.exports


/***/ })

},[291]);
//# sourceMappingURL=app.058bc249df93eaa5d913.js.map