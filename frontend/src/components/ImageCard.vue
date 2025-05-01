<script setup>
import {ref, computed, useTemplateRef, onMounted} from 'vue'


const props = defineProps(['imgSpec', 'index', 'columns', 'rootURL'])
defineEmits(['starred', 'starRemoved'])

const hover = ref(false)
const starred = ref(false)
const downloadOptions = ref('fits')
const imageRef = useTemplateRef('imageRef')

const imagePath = computed(() => `${props.rootURL}api/image/${props.imgSpec.image}.jpg`)
const starImg = computed(() => `../../public/star${starred.value ? "-fill" : ""}.png`)
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
        units.pop()
    }
    return `${exp.toFixed(1)} ${units[0]}`
})
const tempWithUnit = computed(() => {
    const temp = parseFloat(props.imgSpec['temp'])
    return `${temp.toFixed(1)}°C`
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
        await new astro.FITS(fitsPath, toPNG)
    } else if (downloadOptions.value === 'tiff') {
        await new astro.FITS(fitsPath, toTiff)
    }
}

function loadFits(self) {
    const hdu = self.getHDU();

    const header = hdu.header;
    const data = hdu.data;

    const width = header.get('NAXIS1');
    const height = header.get('NAXIS2');
    const bitpix = header.get('BITPIX');

    const array = bitpix === 16 ? new Uint16Array(data.buffer) : new Uint8Array(data.buffer);

    return [array, width, height, header];
}

function toTiff() {
    const [array, width, height, _] = loadFits(this);

    let typedArray = new Uint8Array(array);
    let bitsPerSample = [16];
    let sampleFormat = [1]; // unsigned integer

    const ifd = {
        width,
        height,
        bitsPerSample,
        samplesPerPixel: 1,
        compression: 1,
        photometricInterpretation: 1, // 1 = BlackIsZero
        data: typedArray,
        sampleFormat,
    };

    const tiffBuffer = UTIF.encodeImage(array, width, height);

    const blob = new Blob([new Uint8Array(tiffBuffer)], { type: 'image/tiff' });

    // Trigger download
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = 'converted.tiff';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

function normalizeTo8Bit(input, bitDepth) {
    if (bitDepth === 8) return new Uint8ClampedArray(input); // no change
    if (bitDepth === 16) {
        const max = 65535;
        const normalized = new Uint8ClampedArray(input.length);
        for (let i = 0; i < input.length; i++) {
            normalized[i] = input[i] / max * 255;
        }
        return normalized;
    }
    throw new Error("Only 8-bit or 16-bit inputs supported.");
}

function imageArrayToImageData(data, width, height, channels = 1, bitDepth = 8) {
    const normalized = normalizeTo8Bit(data, bitDepth);
    const rgba = new Uint8ClampedArray(width * height * 4);

    let size = width * height;

    for (let ch = 0; ch < channels; ch++) {
        for (let i = 0; i < size; i++) {
            let x = i % width;
            let y = Math.floor(i / width);

            rgba[ch + y * 4 + x * 4 * width] = normalized[i + ch * size]
            if (ch === 0) {
                rgba[3 + y * 4 + x * 4 * width] = 255; // fully opaque
            }
        }
    }

    for (let i = 0; i < width * height; i++) {
        const base = i * channels;
        const r = normalized[base] ?? 0;
        const g = channels >= 3 ? normalized[base + 1] ?? r : r;
        const b = channels >= 3 ? normalized[base + 2] ?? r : r;

        rgba[i * 4]     = r;
        rgba[i * 4 + 1] = g;
        rgba[i * 4 + 2] = b;
        rgba[i * 4 + 3] = 255; // fully opaque
    }

    return new ImageData(rgba, width, height);
}

function toPNG() {
    const [array, width, height, header] = loadFits(this);
    const canvas = document.createElement("canvas");
    canvas.width = width;
    canvas.height = height;

    const ctx = canvas.getContext("2d");
    const imageData = imageArrayToImageData(array, width, height, header.get("NAXIS"), header.get("BITPIX"));
    ctx.putImageData(imageData, 0, 0);

    canvas.toBlob((blob) => {
        const a = document.createElement("a");
        a.href = URL.createObjectURL(blob);
        a.download = "converted.png";
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    }, "image/png");
}

onMounted(() => {

    const utif = document.createElement('script')
    utif.src = 'https://cdn.jsdelivr.net/npm/utif@3.1.0/UTIF.js'
    document.head.appendChild(utif)
})

</script>

<template>
    <div class="card-container" @mouseenter="hover=true" @mouseleave="hover=false">
        <div class="card" :class="{flipped: hover}">

            <! -- Front Side -->
            <div class="card-front">
                <img v-if="isFlipped" :src="imagePath" alt="" ref="imageRef" @click="onImageClicked"/>
                <div id="info">
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
                    <p>Temp/Humidity: {{tempWithUnit}}/{{imgSpec["humidity"]}}%</p>
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
}

#selector {
    gap: 10px;
    display: flex;
    align-items: center;
}
</style>
