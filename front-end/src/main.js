import { createApp } from 'vue';
import App from './App.vue';
import router from './router'; // 确保引入路由
import ElementPlus from 'element-plus';
import 'element-plus/dist/index.css'; // 引入 Element Plus 的样式
import axios from 'axios'; // 引入 axios

// 设置全局的基础URL
axios.defaults.baseURL = 'http://localhost:5000';

// 可选：将 axios 挂载到 Vue 实例上，以便在组件中直接使用
const app = createApp(App);
app.config.globalProperties.$axios = axios; // 让所有组件都可以通过 this.$axios 使用 axios

app.use(ElementPlus);
app.use(router); // 注册路由
app.mount('#app');
