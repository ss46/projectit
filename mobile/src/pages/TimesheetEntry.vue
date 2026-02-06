<template>
    <div v-if="uploading" class="flex h-80 items-center justify-center">
        <Spinner class=" h-12"></Spinner>
    </div>
    <div v-else>
        <div class=" pt-7 text-right pr-7" v-if="!showCamera">
            <PrimaryButton @click="showCamera = true" :disabled="taskName == ''" :name="actionName"></PrimaryButton>
        </div>
        <div v-if="!showCamera">
            <div v-if="actionName == 'Check-In'">
                <div class=" pt-7 pl-6 pr-6 font-[Inter] font-[600]">
                    <TaskList :tasks="taskResource.data || []"
                        @select="handleTaskSelection" />
                </div>
            </div>
            <div v-else class=" pl-6 pr-6 pt-7 pb-4">
                <div v-if="taskResource.loading" class="flex h-80 items-center justify-center">
                    <Spinner class=" h-12"></Spinner>
                </div>
                <div v-else class="bg-[#B9C8EA] pt-3 pb-3 pl-4 pr-3 rounded-t-md flex gap-3">
                    <ProjectOutline class=" h-6 w-6"></ProjectOutline>
                    <p class="text-[#4A6BB6] font-[600] font-[Inter]"> {{ taskName }}</p> 
                </div>
                <div
                    class="bg-[#F5F8FF] pl-4 pr-3 pt-5 pb-3 rounded-b-md border-[#B9C8EA] border-x-2 border-b-2 flex flex-col gap-3">
                    <p> Check-In Time : {{ dayjs(timesheetDetails.from_time).format("hh:mm:ss a") }}</p>
                    <div @click="showCaption = true"
                        class="bg-white shadow-[0_4px_4px_rgba(0,0,0,0.25)] rounded-sm pt-3 pb-3 pl-2 pr-2 flex gap-2">
                        <FeatherIcon name="download" class="h-6 w-6" />
                        <p>Task Status Update</p>
                    </div>
                    <div v-if="showCaption" class="text-center flex flex-col gap-3">
                        <textarea v-model="caption"></textarea>
                        <div>
                            <PrimaryButton @click="showCamera = true; cameraMode = 'Upload'" name="Upload">
                            </PrimaryButton>
                        </div>
                    </div>
                </div>
            </div>
            <div class=" pl-6 pr-6 pt-7 pb-4" v-if="taskInstruction">
                <Instructions :task="taskInstruction"></Instructions>
            </div>
        </div>
    </div>

    <div v-if="showError">
        <ErrorMessage @dialog-event="showError = $event" :error-message="errorMessage"></ErrorMessage>
    </div>
</template>
<script setup>
import { ref, onMounted, watch, toRaw } from 'vue';
import { createResource, createListResource, toast, FeatherIcon, Spinner } from 'frappe-ui';
import { FileAttachment } from '../composables';
import ErrorMessage from '../components/ErrorMessage.vue';
import TaskList from '../components/TaskList.vue';
import PrimaryButton from '../components/PrimaryButton.vue';
import dayjs from 'dayjs';
import ProjectOutline from './icons/ProjectOutline.vue'
import customParseFormat from "dayjs/plugin/customParseFormat";
import Instructions from './Instructions.vue';
import { showCamera, cameraMode, imageFile } from '../data/camera_context';
import { sessionResource } from '../data/session';

const employee = sessionResource.data.employee_id

watch(imageFile,() =>{
    handleImageCapture(imageFile.value)
}
)
dayjs.extend(customParseFormat);

onMounted(async function () {
    timesheet.update({
        fields: ["name", "time_logs.from_time", "time_logs.project", "time_logs.task", "note", "parent_project.project_name"],
        filters: {
            employee: employee,
            docstatus: 0,
            start_date: dayjs().format('YYYY-MM-DD')
        },
    })
    timesheet.fetch()
    await taskResource.fetch()
    console.log("Tut perezugruzka: ", taskResource.data)
    uploading.value = false
    if (taskResource.data.length === 0) {
        taskResource.value = false
    }
})
const projectName = ref('')
const taskName = ref('')
const taskId = ref('')
const taskStatus = ref('')
const timesheetDetails = ref({})
const projectId = ref('')
const actionName = ref('Check-In')
const taskInstruction = ref(null)
cameraMode.value = 'Check-In'

const checkInImage = ref([])

const errorMessage = ref('')
const showError = ref(false)

const showCaption = ref(false)
const caption = ref('')

const instructions = ref({})

const timesheetEntry = ref({})

const uploading = ref(true)

const employeeCheckInResource = createListResource({
    doctype: "Employee Checkin",
    insert: {
        onSuccess() {
            toast({
                title: "Success",
                text: actionName.value === "Check-Out" ? "Checked-In" : "Checked-Out",
                icon: "check-circle",
                position: "bottom-center",
                iconClasses: "text-blue-500",
            });
            uploading.value = false
        }
    }
})

async function get_current_location() {
    if ("geolocation" in navigator) {
        navigator.geolocation.getCurrentPosition(
            (position) => {
                insertCheckIns(position.coords.latitude, position.coords.longitude)
            },
            (error) => {
                errorMessage.value = error.message
                showError.value = true
                uploading.value = false
            }
        )
    }
    else {
        errorMessage.value = "Geolocation is not supported by your device"
        showError.value = true
        uploading.value = false
    }
}

async function insertCheckIns(latitude, longitude) {
    let time = actionName.value === "Check-Out" ? timesheetEntry.value.time_logs[0].from_time : timesheetEntry.value.time_logs[0].to_time
    employeeCheckInResource.insert.submit({
        employee: employee,
        time: time,
        log_type: actionName.value === "Check-Out" ? "IN" : "OUT",
        custom_timesheet: timesheetEntry.value.name,
        device_id: `${latitude},${longitude}`,
        latitude: latitude,
        longitude: longitude
    })
}

const timesheet = createListResource({
    doctype: "Timesheet",
    insert: {
        onSuccess(data) {
            timesheetEntry.value = data
            actionName.value = "Check-Out"
            cameraMode.value = "Check-Out"
            uploadAllAttachments("Timesheet", data.name, checkInImage.value)
            changeStatus(taskId.value, "Working")
            get_current_location()
        },
        onError(e) {
            errorMessage.value = e
            showError.value = true
        }
    },
    setValue: {
        onSuccess(data) {
            if (cameraMode.value === 'Upload') {
                uploading.value = false
                cameraMode.value = 'Check-Out'
                caption.value = ''
                showCaption.value = false
                toast({
                    title: "Success",
                    text: "Additional Photo Uploaded",
                    icon: "check-circle",
                    position: "bottom-center",
                    iconClasses: "text-blue-500",
                });
                timesheet.fetch()
            }
            else {
                timesheetEntry.value = data
                get_current_location()
                changeStatus(taskId.value, "Completed")
                console.log("Bez perezagruzki: ", taskResource.data)
                cameraMode.value = "Check-In"
                actionName.value = "Check-In"
                projectName.value = ''
                taskName.value = ''
                taskInstruction.value = ''
            }
        },
        onError(e) {
            errorMessage.value = e
            showError.value = true
        }
    },
    onSuccess(data) {
        if (data.length) {
            console.log("data: ", data)
            console.log("data[0]: ", data[0])
            actionName.value = "Check-Out"
            cameraMode.value = "Check-Out"
            timesheetDetails.value = data[0]
            projectName.value = data[0].project_name
            taskId.value = data[0].task
            projectId.value = data[0].project
            restoreTask(taskId.value)
            console.log(taskId.value)
        }
    },
    onError(e) {
        errorMessage.value = e
        showError.value = true
    }

})
//Вывод задач
const taskResource = createResource({
    url: "projectit.api.get_employee_tasks",
    makeParams() {
        return {
            employee_id: employee
        }
    },  
})


function handleTaskSelection(task) {
    taskName.value = task.subject
    projectId.value = task.project
    taskId.value = task.name
    taskStatus.value = task.status
    taskInstruction.value = task
}

const taskByIdResource = createResource({
    url: 'frappe.client.get',
    method: 'GET',
})

async function restoreTask(taskId) {
    const task = await taskByIdResource.fetch({
        doctype: 'Task',
        name: taskId
    })

    taskName.value = task.subject
    taskStatus.value = task.status
    taskInstruction.value = task
}

function displayInstructions() {
    let promise = get_instructions(dayjs().format("YYYY-MM-DD"), projectName.value, employee)
    promise
        .then((d) => {
            instructions.value = d
        })
}

const updateTaskStatus = createResource({
    url: 'projectit.api.update_task_status',
    method: 'POST',
})

async function changeStatus(taskId, status) {
    uploading.value = true
    if (status == "Completed") {
        await updateTaskStatus.submit({
            task_id: taskId,
            status: status,
            completed_on: dayjs().format('YYYY-MM-DD')
        })
    await taskResource.fetch() 
    }
    else {
        await updateTaskStatus.submit({
            task_id: taskId,
            status: status,
            completed_on: ''
        })
    }
}

async function uploadAllAttachments(documentType, documentName, attachments) {
    const uploadPromises = attachments.map(async (attachment) => {
        const fileAttachment = new FileAttachment(attachment)
        return fileAttachment
            .upload(documentType, documentName, "")
            .then((fileDoc) => {
                fileDoc.uploaded = true
            })

    })

    await Promise.allSettled(uploadPromises)
}

async function handleImageCapture(file) {
    uploading.value = true
    if (cameraMode.value === 'Check-In') {
        checkInImage.value = [imageFile.value]
        checkIn()
    }
    else {
        await uploadAllAttachments("Timesheet", timesheetDetails.value.name, [imageFile.value])
        if (cameraMode.value === "Upload") {
            additionalImage()

        }
        else {
            checkOut()
        }
    }
}

const workTimings = createResource({
    url: "projectit.api.get_work_time_settings",
})

function checkIn() {
    timesheet.insert.submit({
        // customer: customer.value,
        title: `${taskName.value} [${sessionResource.data.employee_name}]`, //Добавление названия в timesheet
        parent_project: projectId.value,
        employee: employee,
        note: "<p>Check in at " + dayjs().format("hh:mm:ss") + "</p>",
        time_logs: [{
            from_time: dayjs().format('YYYY-MM-DD HH:mm:ss'),
            project: projectId.value,
            task: taskId.value,
        }],
    })
}

function additionalImage() {
    let note = "<br/><p>Additional Photo added at " + dayjs().format("hh:mm:ss A") + (caption.value ? ( " with notes : " + caption.value ) : " with on notes") + "</p>"
    timesheet.setValue.submit({
        name: timesheetDetails.value.name,
        note: timesheetDetails.value.note + note
    })

}

async function checkOut() {
    await workTimings.fetch()
    let time_logs = []
    let start_time = dayjs(workTimings.data.start_time, 'HH:mm:ss')
    let end_time = dayjs(workTimings.data.end_time, 'HH:mm:ss')
    let from_time = dayjs(timesheetDetails.value.from_time)
    let time = dayjs()
    
    if (from_time < start_time && time >= start_time) {
        time_logs.push({
            activity_type: workTimings.data.over_time_activity_type,
            from_time: from_time.format('YYYY-MM-DD HH:mm:ss'),
            to_time: start_time.format('YYYY-MM-DD HH:mm:ss'),
            project: projectId.value,
            task: taskId.value,
        })
        from_time = start_time.add(1, 's')
    }
    if (time >= end_time && from_time < end_time) {
        time_logs.push({
            activity_type: workTimings.data.regular_time_activity_type,
            from_time: from_time.format('YYYY-MM-DD HH:mm:ss'),
            to_time: end_time.format('YYYY-MM-DD HH:mm:ss'),
            project: projectId.value,
            task: taskId.value,
        })
        from_time = end_time.add(1, 's')
    }
    if ((time > end_time && from_time >= end_time) || time <= start_time) {
        time_logs.push({
            activity_type: workTimings.data.over_time_activity_type,
            from_time: from_time.format('YYYY-MM-DD HH:mm:ss'),
            to_time: time.format('YYYY-MM-DD HH:mm:ss'),
            project: projectId.value,
            task: taskId.value,
        })
    }
    if (time <= end_time && from_time >= start_time) {
        time_logs.push({
            activity_type: workTimings.data.regular_time_activity_type,
            from_time: from_time.format('YYYY-MM-DD HH:mm:ss'),
            to_time: time.format('YYYY-MM-DD HH:mm:ss'),
            project: projectId.value,
            task: taskId.value,
        })
    }
    instructions.value = []
    timesheet.setValue.submit({
        name: timesheetDetails.value.name,
        note: timesheetDetails.value.note + "<br/><p> Check Out at " + dayjs().format("hh:mm:ss A") + "</p>",
        time_logs: time_logs,
        docstatus: 1
    })
}
</script>