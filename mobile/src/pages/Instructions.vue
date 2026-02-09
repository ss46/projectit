<!-- <template>
    <div class="bg-[#B9C8EA] pt-3 pb-3 pl-4 rounded-t-md flex gap-3" v-if="props.instructions">
        <InstructionsIcon class="h-6 w-6"></InstructionsIcon>
        <p class="font-[Inter] font-[600] text-[#4A6BB6]">Instructions</p>
    </div>
    <div class="bg-[#F5F8FF] rounded-b-md border-[#B9C8EA] border-b-2 border-x-2">
        <div v-for="instruction in props.instructions" class=" pl-3 pr-5 pt-4 pb-5">
            <div v-for="(i,k) in instruction" class=" pb-5">
                <div class="bg-[#D6E1F9] pt-3 pb-3 pl-5 pr-5 w-[200px] shadow-[0_0_4px_rgba(0,0,0,0.25)]">
                    {{ k === "work_instruction" ? "Project Instructions" : "Specific Instructions "  }}
                </div>
                <div class="bg-[#FFFFFF] pt-2 pb-2 pl-3 pr-3">
                    <div v-if="i">{{ i }}</div>
                    <div v-else> No Instructions Found</div>
                </div>
            </div>
        </div>
    </div>
</template> 
<script setup>
import InstructionsIcon from './icons/InstructionsIcon.vue';

const props = defineProps({
    instructions : Object
})
</script>-->
<template>
    <div v-if="task">
        <!-- Header -->
        <div class="bg-[#B9C8EA] pt-3 pb-3 pl-4 rounded-t-md flex gap-3 items-center">
            <FeatherIcon name="check-square" class="h-5 w-5 text-[#4A6BB6]" />
            <p class="font-[Inter] font-[600] text-[#4A6BB6]">
                Task Details
            </p>
        </div>

        <!-- Body -->
        <div class="bg-[#F5F8FF] rounded-b-md border-[#B9C8EA] border-b-2 border-x-2 p-4">

            <!-- Title -->
            <div class="font-[600] text-[#2F3E63] mb-2 break-words whitespace-normal">
                {{ task.subject }}
            </div>

            <!-- Meta -->
            <div class="text-sm text-[#6B7AA8] mb-3 flex flex-wrap gap-4">
                <span>Status: {{ task.status }}</span>
                <span>Project: {{ task.project_name }}</span>
                <span v-if="task.priority">Priority: {{ task.priority }}</span>
            </div>
            <hr class="mb-3">
            <div class="text-sm text-[#6B7AA8] mb-3 flex flex-col gap-4">
                <span v-if="task.exp_start_date">
                    <span>Start Date: </span>
                    <span>{{ task.exp_start_date }}</span>
                </span>
                <span v-if="task.exp_end_date">
                    <span>End Date: </span>
                    <span>{{ task.exp_end_date }}</span>
                </span>
            </div>

            <!-- Description -->
            <div class="bg-white p-3 rounded shadow-sm">
                <div v-if="task.description" v-html="task.description" />
                <div v-else class="text-gray-400">
                    No description provided
                </div>
            </div>

        </div>
    </div>

    <!-- Empty state -->
    <div v-else class="text-gray-400 p-4">
        No task selected
    </div>
</template>

<script setup>
import { FeatherIcon } from 'frappe-ui'

defineProps({
    task: {
        type: Object,
        required: false,
        default: null
    }
})
</script>