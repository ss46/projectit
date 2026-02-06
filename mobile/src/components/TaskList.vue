<template>
  <div>
    <ul>
      <li
        v-for="task in tasks"
        :key="task.name"
        class="pb-3"
      >
        <div
          @click="handleClick(task)"
          :class="[
            'pt-3 pb-3 pl-4 pr-4 rounded-md cursor-pointer max-w-full break-words whitespace-normal',
            selectedTask === task.name
              ? 'bg-[#4A6BB6] shadow-[0_4px_4px_rgba(0,0,0,0.25)] text-white'
              : 'bg-[#D6E1F9] text-[#4A6BB6]'
          ]"
        >
          <p class="font-[600] break-words whitespace-normal">
            {{ task.subject }}
          </p>

          <p class="text-sm opacity-80 break-words whitespace-normal">
            {{ task.project }} • {{ task.status }}
          </p>

          <p v-if="task.priority" class="text-xs opacity-70 break-words whitespace-normal">
            Priority: {{ task.priority }}
          </p>
        </div>
      </li>
    </ul>

    <div v-if="!tasks.length && !noData" class="bg-[#D6E1F9] pt-4 pb-4 rounded-lg">
      <p class="text-center text-[#4A6BB6] break-words whitespace-normal">
        No Tasks Found
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  tasks: {
    type: Array,
    default: () => []
  },
  noData: Boolean
})

const emit = defineEmits(['select'])
const selectedTask = ref(null)

function handleClick(task) {
  selectedTask.value = task.name
  emit('select', task)
}
</script>
