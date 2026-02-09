<template>
  <div class="pl-2 pr-2 pt-5 pb-3">
    <ListView
      :listData="rows"
      :header="timesheetHeader"
    />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { createListResource, createResource } from 'frappe-ui'
import ListView from '../components/ListView.vue'
import { sessionResource } from '../data/session'

const employee = computed(() => sessionResource.data?.employee_id)

const timesheetHeader = [
  'Date',
  'Task',
  'Activity Type',
  'Hours',
]

const taskSubjects = ref({})

const tasksResource = createResource({
  url: 'frappe.client.get_list',
  makeParams() {
    return {
      doctype: 'Task',
      fields: ['name', 'subject'],
      limit_page_length: 1000,
    }
  },
  onSuccess(data) {
    taskSubjects.value = Object.fromEntries(
      data.map(t => [t.name, t.subject])
    )
  },
  auto: true,
})

const timesheetResource = createListResource({
  doctype: 'Timesheet',
  fields: [
    'start_date',
    'time_logs.task',
    'time_logs.activity_type',
    'time_logs.hours',
    'modified',
  ],
  filters: {
    employee: employee,
  },
  orderBy: 'modified desc',
  transform(data) {
    console.log(data)
    return data.map(row => ({
      date: formatDate(row.start_date),
      task:
        taskSubjects.value[row.task] ??
        row.task ??
        '',
      activity_type: row.activity_type ?? '',
      hours: row.hours.toFixed(1) ?? 'None',
    }))
  },
  auto: true,
})

const rows = computed(() => timesheetResource.data || [])

function formatDate(dateStr) {
  if (!dateStr) return ''

  const d = new Date(dateStr)
  return d.toLocaleDateString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
  })
}
</script>
