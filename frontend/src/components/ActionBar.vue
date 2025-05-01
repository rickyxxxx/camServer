<script setup>
import {ref} from "vue";

import SearchForm from "./SearchForm.vue";

const showForm = ref(false)

function onSearchClicked(){
    showForm.value = true
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

    <SearchForm v-show="showForm" class="searchForm"/>
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
    position: absolute; /* Make the searchForm float */
    z-index: 950; /* Must be higher than actionBar's z-index */
}
</style>