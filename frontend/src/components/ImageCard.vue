<!--
    Created by: Ruitao Xu
    Date: 2025-04-20
    ----------------------------------------------------------------------------------------------
    Description: ImageCard.vue
    This component is used to display an image card with a preview, download options, and metadata.
    It includes a flip animation to show the back side of the card with additional information.
    The card can be starred or unstarred, and the image can be downloaded in different formats.
    -----------------------------------------------------------------------------------------------

-->

<script setup>
import {ref, computed, useTemplateRef} from 'vue'

const props = defineProps(['imgSpec', 'index', 'columns', 'rootURL'])
defineEmits(['starred', 'starRemoved'])

const hover = ref(false)
const starred = ref(false)
const downloadOptions = ref('fits')
const imageRef = useTemplateRef('imageRef')

const imagePath = computed(() => `${props.rootURL}api/image/${props.imgSpec.image}.jpg`)
const starImg = computed(() => `http://camserver.physics.ucsb.edu/static/dist/star${starred.value ? "-fill" : ""}.png`)
const isFlipped = computed(() => Math.floor(props.index / props.columns) % 2 === 0)
const timezone = props.imgSpec.timeZone

const utcDate = new Date(props.imgSpec.datetime).getTime();

// Format UTC
const utcFormatted = computed(() =>{
    return new Intl.DateTimeFormat('en-US', {
        year: 'numeric', month: '2-digit', day: '2-digit',
        hour: '2-digit', minute: '2-digit', second: '2-digit',
        timeZone: 'UTC', hour12: false}
    ).format(utcDate) + " UTC";
});
// Format Local
const localFormatted = computed(() => {
    return new Intl.DateTimeFormat('en-US', {
        year: 'numeric', month: '2-digit', day: '2-digit',
        hour: '2-digit', minute: '2-digit', second: '2-digit',
        timeZone: timezone,
        timeZoneName: 'short',   // this gives "PDT" or "PST" automatically
        hour12: false
    }).format(utcDate);
})

const expWithUnit = computed(() => {
    let units = ['us', 'ms', 's']
    let exp = parseFloat(props.imgSpec['expTime']);
    while (exp >= 1000) {
        exp /= 1000
        units.shift()
    }
    return `${exp.toFixed(1)} ${units[0]}`
})
const tempWithUnit = computed(() => {
    const temp = parseFloat(props.imgSpec['temp'])
    return `${temp.toFixed(1)}°C`
})
const hum = computed(() => {
    const humidity = parseFloat(props.imgSpec['humidity'])
    return `${humidity.toFixed(1)}%`
})

function onImageClicked() {
    // enter fullscreen mode if image is clicked or exit fullscreen mode if already in fullscreen
    if (document.fullscreenElement) {
        document.exitFullscreen().catch(err => console.error(err))
    } else {
        imageRef["value"].requestFullscreen().catch(err => console.error(err))
    }
}

async function onDownloadClicked() {
    alert("download will start shortly")
    const fitsPath = `${props.rootURL}api/image/${props.imgSpec.image}.fits`
    if (downloadOptions.value === 'fits') {
        window.location.href = fitsPath;
    } else if (downloadOptions.value === 'jpg') {
        window.location.href = imagePath.value;
    } else if (downloadOptions.value === 'png') {
        window.location.href = `${props.rootURL}temp/png/${props.imgSpec.image}.fits`
        // await new astro.FITS(fitsPath, toPNG)
    } else if (downloadOptions.value === 'tiff') {
      window.location.href = `${props.rootURL}temp/tiff/${props.imgSpec.image}.fits`
    }
}
</script>

<template>
    <div class="card-container" @mouseleave="hover=false">
        <div class="card" :class="{flipped: hover}">

            <! -- Front Side -->
            <div class="card-front">
                <img v-if="isFlipped" :src="imagePath" alt="" ref="imageRef" @click="onImageClicked"/>
                <div id="info" @click="hover=true">
                    <h2>{{ imgSpec.siteName }}</h2>
                    <p>{{ localFormatted }}</p>
                    <p>{{utcFormatted}}</p>
                </div>
                <img v-if="!isFlipped" :src="imagePath" alt="" ref="imageRef" @click="onImageClicked"/>
            </div>

            <! -- Back Side -->
            <div class="card-back glassyPanel">

                <div class="card-header">
                    <h2>{{imgSpec.siteName}}</h2>
                    <button @click="starred = !starred" class="img-button" title="add to favorites">
                        <img :src="starImg" alt=""
                             @click="starred['value'] ? $emit('starred'): $emit('starRemoved')"/>
                    </button>
                </div>
                <div class="card-detail">
                    <p>{{localFormatted}}</p>
                    <p>{{utcFormatted}}</p>
                    <p>Exp/Gain: {{expWithUnit}}/{{imgSpec["eGain"]}}</p>
                    <p>Temp/Humidity: {{tempWithUnit}}/{{hum}}</p>
                </div>
                <div class="card-actions">
                    <button @click="onImageClicked">Preview</button>
                    <div id="selector">
                        <select v-model="downloadOptions">
                            <option value="fits">FITS</option>
                            <option value="png">PNG</option>
                            <option value="jpg">JPG</option>
                            <option value="tiff">TIFF</option>
                        </select>
                        <button @click="onDownloadClicked">Download</button>
                    </div>
                </div>

            </div>

        </div>
    </div>
</template>


<style scoped>
p {
    margin: 0;
    padding: 0;
}

h2 {
    margin: 0;
    padding: 0;
}

img {
    height: 100%;
    object-fit: contain;
    clip-path: circle(50% at 50% 50%);
    cursor: pointer;
}

.card-container {
    height: 200px;
    flex-grow: 1;
    max-width: 500px;
    min-width: 350px;
    perspective: 600px;

}

.card {
    width: 100%;
    height: 100%;
    display: flex;
    flex-shrink: 0;
    position: relative;
    transform-style: preserve-3d;
    transition: transform 0.6s ease;
}

.card.flipped {
    transform: rotateY(180deg);
}

.card-front, .card-back {
    width: 100%;
    height: 100%;
    position: absolute;
    backface-visibility: hidden;
    display: flex;
    overflow: clip;
}

.card-front {
    color: lightgray;
    background: transparent;
}

.card-back {
    flex-direction: column;
    justify-content: space-between;
    transform: rotateY(180deg);
}

.card-header {
    display: flex;
    flex-shrink: 0;
    justify-content: space-between;
    align-items: center;
    width: 100%;
}

.card-actions {
    display: flex;
    flex-shrink: 0;
    justify-content: space-between;
    align-items: center;
    width: 100%;
}

#info {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    width: 100%;
    height: 100%;
    cursor: pointer;
    border: red 1px solid;
}

#selector {
    gap: 10px;
    display: flex;
    align-items: center;
}
</style>
