<script setup>
import {ref, computed, onMounted} from 'vue'

defineEmits(["StarClicked"])

const collapsed = ref(false)
const width = computed(() => {
    return collapsed.value ? '52px' : '300px'
})
const collapsedImg = computed(() => {
    return collapsed.value ? 'http://camserver.physics.ucsb.edu/static/dist/toggle-right.png' : 'http://camserver.physics.ucsb.edu/static/dist/toggle-left.png'
})

onMounted(() => {
    collapsed.value = true
})
</script>

<template>
    <div id="sidebar" class="sidebar glassyPanel" :style="{ width }">
        <!-- action buttons -->
        <div id="sidebar-actionbar">
            <button id="sidebar-collapse-btn" class="img-button" title="collapse" @click="collapsed = !collapsed">
                <img :src="collapsedImg" alt=""/>
            </button>
            <div>
                <button v-show="!collapsed" id="sidebar-help-btn" class="img-button" title="help">
                    <img src="http://camserver.physics.ucsb.edu/static/dist/help.png" alt=""/>
                </button>
                <button v-show="!collapsed" id="sidebar-more-btn" class="img-button" title="more">
                    <img src="http://camserver.physics.ucsb.edu/static/dist/more.png" alt=""/>
                </button>
            </div>
        </div>
        <h1 v-show="!collapsed">Search History</h1>
        <label v-show="!collapsed" id="search-field" class="search-field">
            <img src="http://camserver.physics.ucsb.edu/static/dist/search.png" alt="">
            <input type="text" placeholder="Search here">
        </label>

        <!-- Search History -->
        <div id="search-history">
            <div v-show="!collapsed" class="quick-search" @click="$emit('StarClicked')">
                <img src="http://camserver.physics.ucsb.edu/static/dist/star-fill.png" alt="">
                <span>Starred</span>
            </div>
        </div>
    </div>
</template>

<style scoped>
div {
    display: flex;
}

.sidebar {
    display: flex;
    flex-direction: column;
    flex-shrink: 0;
    position: fixed;
    box-sizing: border-box;
    top: 0;
    left: 0;
    width: 300px;
    height: calc(100% - 20px);
    margin: 10px;
    z-index: 1000;
    color: lightgray;
    transition: width 0.3s ease-in-out;
}

#sidebar-actionbar {
    display: flex;
    justify-content: space-between;
}

#sidebar-actionbar div {
    gap: 10px;
}


.search-field {
    display: flex;
    padding: 0 10px;
    transition: transform 0.3s ease-in-out;

}

.search-field input {
    width: 100%;
    height: 20px;
    padding: 5px 5px 5px 30px;
    border-radius: 15px;
    border: none;
    background: rgba(255, 255, 255, 0.6);
    color: #363636;

    transition: transform 0.3s ease-in-out,
    background-color 0.3s ease;

}

.search-field input:hover {
    background: rgba(255, 255, 255, 0.8);
}

.search-field img {
    position: absolute;
    width: 14px;
    height: 14px;
    padding: 8px;
}

.quick-search{
    margin-top: 10px;
    width: 100%;
    border-radius: 10px;
    align-content: center;
    justify-items: center;
}

.quick-search:hover {
    background: rgba(255, 255, 255, 0.2);
}

.quick-search img {
    width: 40px;
    height: 40px;
}

span {
    display: flex;
    align-items: center;
    justify-content: center;
}
</style>