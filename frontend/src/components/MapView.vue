<template>
    <div :id="`map-${mapId}`" class="map-container"></div>
</template>

<script setup>
import { onMounted } from 'vue'
import * as L from 'leaflet'
import 'leaflet/dist/leaflet.css'

const props = defineProps({
    lat: Number,
    lon: Number,
    mapId: String  // this must be unique per tab
})

onMounted(() => {
    const map = L.map(`map-${props.mapId}`).setView([props.lat, props.lon], 13)

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map)

    L.marker([props.lat, props.lon]).addTo(map)
})
</script>

