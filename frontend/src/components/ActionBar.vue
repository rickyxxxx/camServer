<script setup>
import {computed, defineEmits, onMounted, ref} from "vue";
import axios from "axios";

const showForm = ref(false)

function onSearchClicked(){
  window.scrollTo({ top: 0, behavior: 'smooth' });

  showForm.value = true
}

const emit = defineEmits(["searchClicked"])

const siteList = ref([])
const isPickerInRange = ref(false)

const selectedDates = ref(null)
const selectedTime = ref("all")
const selectedSite = ref(null)

const pickerLabel = computed(() => {
  return isPickerInRange.value ? 'Pick a date' : 'Pick a range'
})
const pickerType = computed(() => {
  return isPickerInRange.value ? 'date' : 'daterange'
})

function loadSites() {
  axios.get('http://camserver.physics.ucsb.edu/api/sites')
      .then(response => {
        for (let i = 0; i < response.data.length; i++) {
          response.data[i].siteName = response.data[i].index + ". " + response.data[i].siteName
        }
        siteList.value = response.data
      })
      .catch(error => {
        console.error('Error fetching images:', error)
      })
}

function onPickerClicked() {
  isPickerInRange.value = !isPickerInRange.value
  selectedDates.value = null
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

function onCancelClicked(){
  selectedSite.value = null
  selectedDates.value = null
  selectedTime.value = "all"
  isPickerInRange.value = false
  showForm.value = false
}

function onGoClicked() {
  showForm.value = false;
  let siteId = null;
  for (let i = 0; i < siteList.value.length; i++) {
    if (siteList.value[i].siteName === selectedSite.value) {
      siteId = siteList.value[i].id;
      break;
    }
  }
  emit('searchClicked', {
    selectedDates: selectedDates.value,
    selectedTime: selectedTime.value,
    selectedSite: siteId,
  });
}
</script>

<template>
    <div class="actionBar glassyPanel">
        <button @click="onSearchClicked">Filter</button>
        <div>
            <button>log in</button>
            <button>sign up</button>
        </div>
    </div>

    <div v-show="showForm" class="searchForm glassyPanel">
        <el-radio-group v-model="selectedTime" >
              <el-radio-button value="all">All Day</el-radio-button>
              <el-radio-button value="day">Day time</el-radio-button>
              <el-radio-button value="night">Night time</el-radio-button>
        </el-radio-group>
        <div class="datePicker">
            <el-button @click="onPickerClicked">
              {{pickerLabel}}
            </el-button>

            <el-date-picker
                v-model="selectedDates"
                :type="pickerType"
                :placeholder="pickerType === 'datetime' ? 'Pick a datetime' : 'Pick a range'"
                range-separator="To"
                start-placeholder="Start datetime"
                end-placeholder="End datetime"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                :clearable="true"
            />
        </div>
        <el-autocomplete
            v-model="selectedSite"
            :fetch-suggestions="querySearch"
            value-key="siteName"
            placeholder="Search for a camera"
            clearable
        />
        <div>
            <el-button @click="onGoClicked">go</el-button>
            <el-button @click="onCancelClicked">cancel</el-button>
        </div>
    </div>
</template>

<style scoped>
.actionBar {
    display: flex;
    justify-content: space-between;
    position: sticky;
    width: 100%;
    top: 10px;
    z-index: 900;
}

div {
    display: flex;
    gap: 10px;
}

.searchForm {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    position: sticky; /* Make the searchForm float */
    z-index: 950; /* Must be higher than actionBar's z-index */
}
</style>