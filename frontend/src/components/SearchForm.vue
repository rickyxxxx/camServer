<script setup>
import {ref, onMounted, computed} from "vue";

const siteName = ref(null)
const siteList = ref([])

function loadSites() {
    siteList.value = [
        {siteName: '1.UCSB Broida Roof -C', lat: 34.1234, lon: -119.1234},
        {siteName: '2.UCSB Broida Roof -M', lat: 34.1234, lon: -119.1234},
        {siteName: '3.Goleta High School -C', lat: 54.1234, lon: -109.1234},
        {siteName: '4.Santa Barbara Library -C', lat: 12.1234, lon: -69.1234},
    ]
}

onMounted(() => {
    loadSites()
})

const querySearch = (queryString, callback) => {
    const results = queryString
        ? siteList.value.filter((site) => {
            return site.siteName.toLowerCase().includes(queryString.toLowerCase())
        })
        : siteList.value
    console.log(results)
    callback(results)
}

</script>

<template>
    <div class="from glassyPanel">
        <el-autocomplete
            v-model="siteName"
            :fetch-suggestions="querySearch"
            value-key="siteName"
            placeholder="Search for a camera"
            clearable
        />
    </div>


<!--    <div class="searchPanel">-->
<!--        <div class="datePicker">-->


<!--            <el-button @click="onPickerClicked">-->
<!--                {{pickerLabel}}-->
<!--            </el-button>-->

<!--            <el-date-picker-->
<!--                v-model="dateValue"-->
<!--                :type="pickerType"-->
<!--                :shortcuts="shortcuts"-->
<!--                :placeholder="pickerType === 'datetime' ? 'Pick a datetime' : 'Pick a range'"-->
<!--                range-separator="To"-->
<!--                start-placeholder="Start datetime"-->
<!--                end-placeholder="End datetime"-->
<!--                format="YYYY-MM-DD HH:mm"-->
<!--                value-format="YYYY-MM-DDTHH:mm:ss"-->
<!--                :clearable="true"-->
<!--            />-->
<!--        </div>-->

<!--    </div>-->
</template>

<style scoped>

</style>