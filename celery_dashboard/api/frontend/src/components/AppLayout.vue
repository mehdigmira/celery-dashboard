<template>
  <div>
    <snackbar></snackbar>
    <run-task-dialog></run-task-dialog>
    <side-menu></side-menu>
    <slot></slot>
  </div>
</template>

<script>
import SideMenu from "./SideMenu";
import Snackbar from './Snackbar'
import RunTaskDialog from './RunTaskDialog'

export default {
    name: 'app-layout',
    components: {
        SideMenu, Snackbar, RunTaskDialog
    }
}
</script>

<style>
.with-graph {
    padding-top: 5px;
}
</style>