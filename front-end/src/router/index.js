import {createRouter, createWebHistory} from 'vue-router';
import Home from '@/views/Home.vue';
import Records from '@/views/Records.vue';
import LoginRegister from '@/views/LRView.vue';
import Charts from "@/views/Charts.vue";
import Reports from "@/views/Reports.vue";

const routes = [

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
        path: '/reports',
        name: 'Reports',
        component: Reports,
    },
    {
        path: '/:pathMatch(.*)*',
        redirect: '/loginRegister',
    }
];

const router = createRouter({
    history: createWebHistory(),
    routes,

});

export default router;
