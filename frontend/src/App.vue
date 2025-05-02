<script setup>
import {ref, onMounted, onBeforeUnmount, useTemplateRef} from 'vue'
import axios from 'axios'

import ImageCard from './components/ImageCard.vue'
import Sidebar from "./components/Sidebar.vue";
import ActionBar from "./components/ActionBar.vue";


let resizeObserver
let rootURL = 'http://camserver.physics.ucsb.edu/'

const numberOfColumns = ref(0)
const images = ref([])
const starList = ref([]) // stores the UIDs of starred images
const container = useTemplateRef("container")
let condition = ''

let lastUID = null

async function loadMore() {
    axios.get(`${rootURL}api/query`, {
        params: {"lastUID": lastUID, "conditions": condition}
    }).then(response => {
        images.value.push(...response.data)
        const UIDs = response.data.map(image => image['UID'])
        lastUID = Math.min(...UIDs); // Use spread operator with Math.min
    }).catch(error => {
        console.error('Error fetching images:', error)
    })
}

function clearSearch() {
    images.value = []
    lastUID = null
}

function onStarClicked() {
    clearSearch()
    images.value = starList.value
}

function onCardStarred(imgSpec) {
    starList.value.push(imgSpec)
    console.log(starList.value)
}

function updateNumberOfColumns() {
    if (!container["value"])    // make sure the image container is loaded
        return

    const firstItem = container["value"].querySelector('.grid-item');
    if (!firstItem)             // make sure there are items in the container
        return

    const containerWidth = container["value"].clientWidth;
    const itemWidth = firstItem.clientWidth;
    numberOfColumns.value = Math.floor(containerWidth / itemWidth);
}

function handleScroll() {
    const scrollPosition = window.innerHeight + window.scrollY
    const bottom = document.documentElement.offsetHeight

    if (scrollPosition >= bottom) {
        loadMore() // emit event to parent to fetch more data
    }
}

function onSearchClicked(args){
    condition = ""
    if (args['selectedTime'] === 'day'){
        condition += "IsDayTime = 1"
    } else if (args['selectedTime'] === 'night'){
        condition += "IsDayTime = 0"
    }

    if (args['selectedSite']){
        if (condition !== "")
            condition += " AND "
        condition += `Images.CamId = '${args['selectedSite']}'`
    }

    if(args['selectedDates']) {
      if (args['selectedDates'].length > 0) {
        if (condition !== "")
          condition += " AND "
        const dates = args['selectedDates']
        if (typeof dates === 'object' && dates[0] && dates[1]) {
          const startDate = dates[0];
          const endDate = dates[1];
          condition += `Timestamp >= '${startDate}' AND Timestamp <= '${endDate}'`;
        }
        // Check if dates is a single date string
        else if (typeof dates === 'string') {

          condition += `CAST(Timestamp AS DATE) = '${dates}'`;
        }
      }
    }

    console.log(condition)
    clearSearch()
    loadMore()
}

onMounted(() => {
    resizeObserver = new ResizeObserver(updateNumberOfColumns);
    if (container["value"]) {
        // watch for the size change of the container
        resizeObserver.observe(container["value"])
        updateNumberOfColumns()
    }
    loadMore()
    window.addEventListener('scroll', handleScroll)
})

onBeforeUnmount(() => {
    if (container["value"]) {
        resizeObserver.unobserve(container["value"])
    }
    window.removeEventListener('scroll', handleScroll)
})
</script>

<template>
    <Sidebar @star-clicked="onStarClicked"/>
    <div class="container" ref="container" @resize="updateNumberOfColumns">
        <ActionBar @search-clicked="onSearchClicked"/>
        <div class="spacer">
            <div class="imgContainer">
                <ImageCard
                    v-for="(imageSpec, index) in images"
                    :key="index"
                    :imgSpec="imageSpec"
                    :index="index"
                    :columns="numberOfColumns"
                    class="grid-item"
                    :rootURL="rootURL"
                    @starred="onCardStarred(imageSpec)"
                />
            </div>
        </div>
    </div>
</template>

<style scoped>
.container {
    margin: 0 30px 0 85px;

}

.spacer {
    width: 100%;
    display: flex;
    justify-content: center; /* center horizontally */
}

.imgContainer {
    margin-top: 10px;
    display: flex;
    flex-wrap: wrap;
}
</style>
