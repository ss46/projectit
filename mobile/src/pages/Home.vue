<template>
  <div class="sm:w-96 font-[Inter]">
    <div class="pt-[16px] flex flex-col items-center justify-center">
      <div class="w-[322px] h-11 bg-[#F2F2F2] flex items-center justify-center shadow-[0_4px_4px_rgba(0,0,0,0.25)]">
        <p class="text-[#4A6BB6] font-[800] text-2xl">ProjectIT</p>
      </div>
      <div class="pt-[30px]">
        <div class="text-center">
          <img src="../images/home_page.png" />
        </div>
      </div>
    </div>

    <!-- loader пока подгружаются модули -->
    <div v-if="sessionLoading || modulesLoading">
      Loading...
    </div>
    <!-- нет сотрудника -->
    <div v-else-if="!employee" class="pt-10 pl-6 pr-6">
      <div class="pt-3 pb-4 border-2 border-[#B9C8EA] text-center rounded-lg bg-[#D6E1F9] font-[Inter] font-[600]">
        You are not an Employee
      </div>
    </div>
    <!-- нет модулей -->
    <div v-else-if="!hasModules" class="pt-10 pl-6 pr-6">
      <div class="pt-3 pb-4 border-2 border-[#B9C8EA] text-center rounded-lg bg-[#D6E1F9] font-[Inter] font-[600]">
        You have no modules assigned
      </div>
    </div>
    <!-- есть сотрудник и модули -->
    <div v-else>
      <div class="pt-15 flex justify-evenly">
        <ThemeButton v-if="modules.includes('workit')" name="WorkIT" @click="router.push({ name: 'WorkIT' })" />
        <ThemeButton v-if="modules.includes('manageit')" name="ManageIT" @click="router.push({ name: 'ManageIT' })" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { createResource } from 'frappe-ui'
import { useRouter } from 'vue-router'
import ThemeButton from '../components/ThemeButton.vue'
import { sessionResource } from '../data/session'
import { computed, ref, watch } from 'vue'

const router = useRouter()

const employee = ref(null)
const modules = ref([])

// модули
const mobileModules = createResource({
  type: 'POST',
  url: 'projectit.api.get_modules_for_router',
  auto: true,
  onSuccess(data) {
    modules.value = Array.isArray(data) ? data : []
    console.log("modules.value in mm: ", modules.value)
  },
  onError(error) {
    console.log('modules fetch failed', error)
  }
})

watch(
  () => sessionResource.data,
  (newData) => {
    employee.value = newData?.employee_id || null
  },
  { immediate: true }
)
console.log("employee.value: ", employee.value)

const hasModules = computed(() => modules.value.length > 0)

const canAccessWorkIT = computed(() => modules.value.includes('WorkIT'))
const canAccessManageIT = computed(() => modules.value.includes('ManageIT'))
</script>
