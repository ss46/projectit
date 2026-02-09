<template>
  <div class="w-full space-y-3">
    <!-- Action button -->
    <div v-if="showActionButton" class="flex justify-end">
      <Button
        variant="solid"
        theme="blue"
        :disabled="!selectedRow"
        @click="handleAction()"
      >
        {{ actionButtonLabel }}
      </Button>
    </div>

    <!-- Table -->
    <table class="w-full table-fixed border-collapse shadow-[0_4px_4px_rgba(0,0,0,0.25)]">
      <tbody>
        <!-- Header -->
        <tr class="bg-[#4A6BB6]">
          <td
            v-for="h in header"
            :key="h"
            class="pt-2 pb-2 pl-2 pr-2 border border-white"
          >
            <p class="text-center text-white font-[600] break-words whitespace-normal">
              {{ h }}
            </p>
          </td>
        </tr>

        <!-- Rows -->
        <tr
        v-for="(line, index) in listData"
        :key="index"
        class="cursor-pointer transition-colors"
        :class="rowClasses(line,index)"
        >
            <td
            v-for="(v, k) in visibleEntries(line)"
            :key="k"
            tabindex="0"
            @focus="selectRow(line)"
            @click="selectRow(line)"
            @keydown.enter="handleAction"
            class="pt-2 pb-2 pl-2 pr-2 border border-[#C4C4C4]
                    break-words whitespace-normal min-w-0 align-top
                    outline-none transition-colors"
            :class="tdClasses(line)"
            >
            {{ k.includes('date') ? dayjs(v).format('DD/MM/YY') : v }}
            </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import dayjs from 'dayjs'
import { ref } from 'vue'
import { Button } from 'frappe-ui'

const props = defineProps({
  header: Array,
  listData: Array,
  hiddenFields: {
    type: Array,
    default: () => ['id'],
  },
  showActionButton: {
    type: Boolean,
    default: false
  },
  actionButtonLabel: {
    type: String,
    default: 'Open'
  }
})

const emit = defineEmits(['action'])

const selectedRow = ref(null)

function visibleEntries(line) {
  const hidden = Array.isArray(props.hiddenFields)
    ? props.hiddenFields
    : []

  return Object.fromEntries(
    Object.entries(line).filter(
      ([key]) => !hidden.includes(key)
    )
  )
}

function selectRow(row) {
  selectedRow.value = row
}

function handleAction() {
  if (!selectedRow.value) return
  emit('action', selectedRow.value)
}

function rowClasses(row, index) {
  return [
    index % 2 === 0 ? 'bg-white' : 'bg-[#F4F8FF]',
    'hover:bg-[#D6E1F9]',
  ]
}
function tdClasses(row) {
  if (selectedRow.value === row) {
    return 'bg-[#4A6BB6] text-white'
  }
}

</script>
