import { createApp } from 'vue';
import App from './App.vue';
import router from './router'; // 确保引入路由
import ElementPlus from 'element-plus';
import 'element-plus/dist/index.css'; // 引入 Element Plus 的样式

const app = createApp(App);

app.use(ElementPlus)
app.use(router); // 注册路由
app.mount('#app');
