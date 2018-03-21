// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from "vue";
import Vuetify from 'vuetify'
import Jobs from "./routes/Jobs"
import Queues from "./routes/Queues"
import Workers from "./routes/Workers"
import VueRouter from 'vue-router'

import "../node_modules/ag-grid/dist/styles/ag-grid.css";
import "../node_modules/ag-grid/dist/styles/ag-theme-material.css";
import "../node_modules/vuetify/dist/vuetify.min.css";

Vue.config.productionTip = false;
Vue.use(Vuetify);
Vue.use(VueRouter);

const routes = [
    { path: '/jobs', name: 'jobs', component: Jobs },
    { path: '/queues', name: 'queues', component: Queues },
    { path: '/workers', name: 'workers', component: Workers },
    { path: '*', redirect: '/workers' }
];

const router = new VueRouter({
    routes
});

/* eslint-disable no-new */
new Vue({
    router
}).$mount('#app')
