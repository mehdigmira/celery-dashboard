<template>
    <div>
        <v-navigation-drawer temporary absolute light v-model="drawer">
            <v-toolbar flat>
            <v-list>
                <v-list-tile>
                <v-list-tile-title class="title">
                    Celery Dashboard
                </v-list-tile-title>
                </v-list-tile>
            </v-list>
            </v-toolbar>
            <v-divider></v-divider>
            <v-list dense class="pt-0">
            <v-list-tile :to="{name: 'workers'}">
                <v-list-tile-action>
                <v-icon>home</v-icon>
                </v-list-tile-action>
                <v-list-tile-content>
                <v-list-tile-title>Workers</v-list-tile-title>
                </v-list-tile-content>
            </v-list-tile>
            <v-list-tile :to="{name: 'jobs'}">
                <v-list-tile-action>
                <v-icon>grid_on</v-icon>
                </v-list-tile-action>
                <v-list-tile-content>
                <v-list-tile-title>Jobs</v-list-tile-title>
                </v-list-tile-content>
            </v-list-tile>
            <v-list-tile :to="{name: 'queues'}">
                <v-list-tile-action>
                <v-icon>compare_arrows</v-icon>
                </v-list-tile-action>
                <v-list-tile-content>
                <v-list-tile-title>Queues</v-list-tile-title>
                </v-list-tile-content>
            </v-list-tile>
            </v-list>
        </v-navigation-drawer>
        <v-toolbar dark color="primary">
            <v-toolbar-side-icon @click.stop="drawer = !drawer"></v-toolbar-side-icon>
            <v-toolbar-title class="white--text">Celery Dashboard</v-toolbar-title>
        </v-toolbar>
    </div>
</template>

<script>
export default {
  name: "side-menu",
  data() {
      return {
          drawer: false
      }
  }
}
</script>
