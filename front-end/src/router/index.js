import { createRouter, createWebHistory } from 'vue-router';
import Home from '@/views/Home.vue';
import Records from '@/views/Records.vue';
import LoginRegister from '@/views/LRView.vue';
import Charts from "@/views/Charts.vue";
import Favorites from "@/views/Favorites.vue";

const routes = [
    {
        path: '/',
        name: 'Home',
        component: Home,
    },
    {
        path: '/loginRegister',
        name: 'LoginRegister',
        component: LoginRegister,
    },
    {
        path: '/records',
        name: 'Records',
        component: Records,
    },
    {
        path: '/charts',
        name: 'Charts',
        component: Charts,
    },
    {
        path: '/favorites',
        name: 'Favorites',
        component: Favorites,
    },
];

const router = createRouter({
    history: createWebHistory(),
    routes,
});

export default router;
