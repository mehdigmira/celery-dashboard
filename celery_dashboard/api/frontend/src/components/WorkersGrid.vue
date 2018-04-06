<template>
    <div>
        <div class="filter-box">
            <v-form ref="form">
                <v-layout row wrap>
                    <v-select
                            label="Refresh interval"
                            v-model="refreshInterval"
                            :items="[{text: '5 seconds', value: 5}, {text: '30 second', value: 30}, {text: '1 minute', value: 60}, {text: '5 minutes', value: 300}]"
                    ></v-select>
                </v-layout>
            </v-form>
        </div>
        <ag-grid-vue class="ag-theme-material grid"
                     :gridOptions="gridOptions">
        </ag-grid-vue>
    </div>
</template>

<script>
    import {AgGridVue} from "ag-grid-vue";
    import {EventBus} from '../utils/bus.js';
    import Vue from "vue";
    import * as $ from 'jquery';
    import 'jquery-sparkline'

    export default {
        name: "workers-grid",
        data() {
            return {
                gridOptions: null,
                loading: false,
                runningPoller: null,
                refreshInterval: 5
            }
        },
        components: {
            AgGridVue
        },
        methods: {
            createColDefs() {
                return [
                    {headerName: "Worker", field: "name"},
                    {headerName: "Broker", field: "broker"},
                    {headerName: "Pool size", field: "poolSize"},
                    {
                        headerName: "Tasks", field: "tasks", cellRenderer(params) {
                            if (!!params.data) {
                                return `<span id="chart-worker-${params.data.pid}"></span>`
                            }
                        }, cellClass: 'with-graph'
                    }
                ];
            },
            poller() {
                if (this.loading) return;
                this.loading = true;
                fetch("/api/workers").then((response) => {
                    this.loading = false;
                    if (response.status !== 200) {
                        EventBus.$emit('snackbar:show', {
                            text: "An error occurred",
                            color: "error",
                            timeout: 2000
                        });
                        let error = new Error(response.statusText);
                        error.response = response;
                        throw error
                    }
                    return response.json();
                }).then((json) => {
                    if (this.gridOptions.api) {
                        this.gridOptions.api.setRowData(json.result);
                        Vue.nextTick(() => {
                            this.gridOptions.api.sizeColumnsToFit();
                            json.result.forEach((worker) => {
                                let taskCounts = []
                                let taskMappings = {}
                                let count = 0
                                Object.keys(worker.tasks).forEach((taskName) => {
                                    taskMappings[count] = taskName
                                    taskCounts.push(worker.tasks[taskName])
                                    count += 1
                                })
                                $(`#chart-worker-${worker.pid}`).sparkline(taskCounts, {
                                    type: 'bar',
                                    height: 100,
                                    barWidth: 10,
                                    tooltipFormat: '{{offset:offset}} ({{value}})',
                                    tooltipValueLookups: {
                                        'offset': taskMappings
                                    }
                                });
                            })
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
            EventBus.$on('workerspolling', this.handlePoller);
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
            Vue.nextTick(() => {
                this.gridOptions.api.sizeColumnsToFit();
            });
        },
        watch: {
            refreshInterval: function () {
                clearInterval(this.runningPoller);
                this.setPoller();
            }
        }
    };
</script>
