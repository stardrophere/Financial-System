import {createApp} from 'vue';
import App from './App.vue';
import router from './router'; // 确保引入路由
import ElementPlus, {ElMessage} from 'element-plus';
import 'element-plus/dist/index.css'; // 引入 Element Plus 的样式
import axios from 'axios'; // 引入 axios

// 设置全局的基础URL
// axios.defaults.baseURL = 'http://10.252.130.135:5000/';
axios.defaults.baseURL = 'http://localhost:5000/';

// 请求拦截器：在每个请求中添加 Authorization 头
axios.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = token;  // 将 token 添加到请求头中
        }
        return config;
    },
    (error) => {
        // 请求错误时的处理
        return Promise.reject(error);
    }
);

// 响应拦截器：处理 401 错误并跳转到登录页
axios.interceptors.response.use(
    (response) => {
        return response;  // 如果响应成功，直接返回响应数据
    },
    (error) => {
        if (error.response && error.response.status === 401) {
            ElMessage.warning("登陆过期, 将自动跳转至登录页面");
            setTimeout(() => {
                window.location.href = '/loginRegister';  // 自动跳转至登录页面
            }, 1500);
        }
        // 其他错误继续返回
        return Promise.reject(error);
    }
);

// 创建 Vue 应用并挂载
const app = createApp(App);

// 将 axios 挂载到 Vue 实例上，以便在组件中直接使用
app.config.globalProperties.$axios = axios;  // 让所有组件都可以通过 this.$axios 使用 axios

app.use(ElementPlus);  // 使用 Element Plus UI 库
app.use(router);  // 注册路由
app.mount('#app');  // 挂载应用到 DOM
