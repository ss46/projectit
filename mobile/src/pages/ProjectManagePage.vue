<template>
  <!-- Верхняя панель -->
  <div class="flex flex-row gap-4 justify-end pb-3">
    <Button variant="outline" @click="collapseAll">Collapse All</Button>
    <Button variant="outline" @click="expandAll">Expand All</Button>
    <Button variant="solid" theme="blue" @click="addProject">
      Add Project
    </Button>
  </div>

  <!-- Список проектов -->
  <div
    v-for="(project, index) in projects"
    :key="project.name"
    class="pt-3"
  >
    <!-- Заголовок проекта -->
    <div
      :class="[
        'flex gap-3 items-center pt-2 pb-2 pl-3 pr-3 border-2 border-[#D6E1F9] cursor-pointer',
        project.dropdown ? 'bg-[#adbde0] rounded-t-md' : 'rounded-md'
      ]"
      @click="toggleProject(index)"
    >
      <FeatherIcon
        class="w-6 h-6"
        :name="project.dropdown ? 'chevron-down' : 'chevron-right'"
      />
      <p class="font-semibold">
        {{ project.project_name }}
      </p>
    </div>

    <!-- Контент проекта -->
    <div
      v-if="project.dropdown"
      class="pt-3 pb-3 pl-4 pr-4 border-2 border-[#D6E1F9] rounded-b-md bg-[#f5ffff]"
    >
      <div class="flex justify-between">
        <p class="text-sm text-gray-500">Руководитель проекта:</p>
        <p v-if="project.full_name"
           class="text-sm text-gray-500">{{ project.full_name }}</p>
        <p v-else class="text-sm text-gray-500">Без руководителя</p>
      </div>
      <div class="py-1">
        <Button size="sm" variant="solid" theme="blue" @click.stop="addTask(project)">
          Add Task
        </Button>
      </div>
      <div class="pt-6">
        <TaskList :tasks="project.tasks" />
        <p
          v-if="!project.tasks.length && project.loaded"
          class="text-sm text-gray-500 pt-2"
        >
          No tasks found
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { createResource, Button, FeatherIcon } from 'frappe-ui'
import { sessionResource } from '../data/session'
import TaskList from '../components/TaskList.vue'

const employee = sessionResource.data

const projectAllocationResource = createResource({
  url: 'projectit.api.get_project_allocation',
  params: {
    user_company: employee.company
  },
  auto: true,
  transform(data) {
    return data.map(p => ({
      ...p,
      dropdown: false,
      tasks: [],
      loaded: false
    }))
  }
})

const projects = computed(() => projectAllocationResource.data || [])

const taskListResource = createResource({
  url: 'frappe.client.get_list',
  method: 'GET'
})

async function toggleProject(index) {
  const project = projects.value[index]
  project.dropdown = !project.dropdown

  if (!project.dropdown || project.loaded) return
  const tasks = await taskListResource.fetch({
    doctype: 'Task',
    filters: JSON.stringify({ project: project.name }),
    fields: JSON.stringify(['*'])
  })
  console.log(tasks)
  project.tasks = tasks.map(t => ({
    ...t,
    project_name: project.project_name
  }))
  project.loaded = true
}

function expandAll() {
  projects.value.forEach(p => (p.dropdown = true))
}

function collapseAll() {
  projects.value.forEach(p => (p.dropdown = false))
}

function addProject() {
  console.log('Add Project clicked')
}

function addTask(project) {
  console.log('Add Task to project:', project.project_name)
}
</script>
