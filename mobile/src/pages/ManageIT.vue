<template>
    <div>
        <div class=" pt-5 pl-5 pr-5 pb-5">
            <ProjectManagePage></ProjectManagePage>
        </div>
    </div>
</template>
<script setup>
import { ref } from 'vue';
import ProjectManagePage from './ProjectManagePage.vue';
import { moduleName } from '../data/module';

moduleName.value = "ManageIT";

</script>