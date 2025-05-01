import { createRouter, createWebHistory } from 'vue-router'

// Import your page components
import Gallery from '../pages/Gallery.vue'

// import HomePage from '@/pages/HomePage.vue'
// import AboutPage from '@/pages/AboutPage.vue'
// import ContactPage from '@/pages/ContactPage.vue'

const routes = [
    { path: '/', component: Gallery },
    { path: '/:pathMatch(.*)*', redirect: '/' }

]

const router = createRouter({
    history: createWebHistory(),
    routes,
})

export default router