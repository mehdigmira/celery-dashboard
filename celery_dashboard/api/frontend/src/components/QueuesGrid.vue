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
        name: "queues-grid",
        data() {
            return {
                gridOptions: null,
                loading: false,
                runningPoller: null,
                dataByQueue: {},
                refreshInterval: 5
            }
        },
        components: {
            AgGridVue
        },
        methods: {
            createColDefs() {
                return [
                    {headerName: "Queue", field: "routing_key"},
                    {headerName: "Started", field: "STARTED"},
                    {headerName: "Queued", field: "QUEUED"},
                    {headerName: "Waiting for retry", field: "RETRY"},
                    {
                        headerName: "Progress", field: "progress", cellRenderer(params) {
                            if (!!params.data) {
                                return `<span id="chart-${params.data.routing_key}"></span>`
                            }
                        }, cellClass: 'with-graph'
                    }
                ];
            },
            poller() {
                if (this.loading) return;
                this.loading = true;
                fetch("/api/queues").then((response) => {
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
                    json.result.forEach((record) => {
                        let queue = record.routing_key;
                        let oldProgress = (this.dataByQueue[queue] || {}).progress || [];
                        oldProgress.unshift(record.ALL);
                        oldProgress = oldProgress.slice(0, 200);
                        this.dataByQueue[queue] = {
                            routing_key: queue,
                            running_jobs: (json[queue] || []).length,
                            progress: oldProgress
                        }
                    });
                    if (this.gridOptions.api) {
                        this.gridOptions.api.setRowData(json.result);
                        Vue.nextTick(() => {
                            this.gridOptions.api.sizeColumnsToFit();
                            Object.keys(this.dataByQueue).forEach((queue) => {
                                $(`#chart-${queue}`).sparkline(this.dataByQueue[queue].progress, {
                                    defaultPixelsPerValue: 1,
                                    height: 100
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
            EventBus.$on('queuespolling', this.handlePoller);
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
