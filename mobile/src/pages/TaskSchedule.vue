<template>
  <div class="pl-3 pr-3 pt-5">
    <ListView
      :listData="tasks"
      :header="tasksHeader"
      :showActionButton="true"
      actionButtonLabel="Details"
      @action="taskSelected"
    />
  </div>

  <Dialog
    v-model="showTaskDetails"
    :options="{
      actions: [{
        label: 'OK',
        variant: 'solid',
        onClick: () => showTaskDetails = false,
      }],
    }"
  >
    <template #body-title>
      <p class="font-mono font-bold text-xl">
        {{ selectedTask?.subject }}
      </p>
    </template>

    <template #body-content>
      <div class="space-y-3">
        <div>
          <b>Status:</b> {{ selectedTask?.status }}
        </div>
        <div v-if="selectedTask?.priority">
          <b>Priority:</b> {{ selectedTask.priority }}
        </div>
        <div v-if="selectedTask?.exp_end_date">
          <b>Due:</b> {{ selectedTask.exp_end_date }}
        </div>

        <div class="bg-white p-3 rounded border">
          <div
            v-if="selectedTask?.description"
            v-html="selectedTask.description"
          />
          <div v-else class="text-gray-400">
            No description
          </div>
        </div>
      </div>
    </template>
  </Dialog>
</template>
<script setup>
import { createResource, Dialog } from 'frappe-ui'
import { ref } from 'vue'
import ListView from '../components/ListView.vue'
import { sessionResource } from '../data/session'

const employee = sessionResource.data.employee_id
const tasks = ref([])
const tasksHeader = ref([
  'Task',
  'Project',
  'Status',
])

const showTaskDetails = ref(false)
const selectedTask = ref(null)
const projectSubjects = ref({})

const projectResource = createResource({
  url: 'frappe.client.get_list',
  makeParams() {
    return {
      doctype: 'Project',
      fields: ['name', 'project_name'],
      limit_page_length: 1000,
    }
  },
  onSuccess(data) {
    projectSubjects.value = Object.fromEntries(
      data.map(p => [p.name, p.project_name])
    )
  },
  auto: true,
})

const tasksResource = createResource({
  url: 'projectit.api.get_employee_tasks',
  makeParams() {
    return {
      employee_id: employee,
    }
  },
  auto: true,
  onSuccess(data) {
    tasks.value = data.map(task => ({
      subject: task.subject,
      project: projectSubjects.value[task.project] ??
               task.project ??
               '',
      status: task.status
    }))
    console.log("task: ", tasks.value)
  },
  onError(error) {
    console.log("Error TasksResource")
  }
})

function taskSelected(row) {
  selectedTask.value = row
  showTaskDetails.value = true
}
</script>
