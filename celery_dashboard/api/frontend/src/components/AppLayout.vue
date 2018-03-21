<template>
  <div>
    <snackbar></snackbar>
    <side-menu></side-menu>
    <slot></slot>
  </div>
</template>

<script>
import SideMenu from "./SideMenu";
import Snackbar from './Snackbar'

export default {
    name: 'app-layout',
    components: {
        SideMenu, Snackbar
    }
}
</script>

<style>
.with-graph {
    padding-top: 5px;
}
</style>