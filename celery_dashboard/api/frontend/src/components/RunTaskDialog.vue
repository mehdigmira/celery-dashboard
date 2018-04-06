<template>
    <v-dialog v-model="show" max-width="500px">
        <v-card>
            <v-card-title>
                Run task
            </v-card-title>
            <v-card-text>
                <v-form v-model="valid" ref="form" lazy-validation>
                    <v-text-field
                            label="Task name"
                            v-model="name"
                            required
                            :rules="rules"
                    ></v-text-field>
                    <v-text-field
                            label="Queue"
                            v-model="queue"
                            required
                            :rules="rules"
                    ></v-text-field>
                    <v-text-field
                            v-model="kwargs"
                            label="Kwargs"
                            multi-line
                            required
                            :rules="kwargsRules"
                    ></v-text-field>
                </v-form>
            </v-card-text>
            <v-card-actions>
                <v-btn color="primary" flat @click.stop="show=false">Close</v-btn>
                <v-btn color="primary" flat @click.stop="sendTask()">Send task</v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>
</template>

<script>
    import {EventBus} from '../utils/bus.js'

    export default {
        name: "run-task-dialog",
        data() {
            return {
                show: false,
                valid: true,
                name: null,
                queue: null,
                kwargs: null,
                rules: [(v) => !!v || 'Field is required'],
                kwargsRules: [(v) => !!v || 'Field is required', (v) => {
                    try {
                        JSON.parse(v);
                    } catch (e) {
                        return 'Must be a json';
                    }
                    return true;
                }]
            }
        },
        created() {
            EventBus.$on('run-task', this.showDialog);
        },
        methods: {
            showDialog() {
                this.show = true;
            },
            sendTask() {
                if (this.$refs.form.validate()) {
                    let kwargs = JSON.parse(this.kwargs);
                    fetch('/api/task', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            task: this.name,
                            queue: this.queue,
                            kwargs: kwargs
                        }),
                        credentials:"include"
                    }).then((response) => {
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
                        EventBus.$emit('snackbar:show', {
                            text: `Task successfully sent`,
                            color: "success",
                            timeout: 3000
                        });
                        this.show = false;
                        this.$router.push({
                            name: 'jobs',
                            query: {
                                taskId: json.taskId
                            }
                        })
                    })
                }
            }
        },
    }
</script>
