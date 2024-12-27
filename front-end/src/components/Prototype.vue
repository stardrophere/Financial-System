<template>
  <div id="app">
    <div>
      <h1>简易记账系统</h1>
      <div v-if="!isLoggedIn">
        <h2>登录</h2>
        <form @submit.prevent="login">
          <input v-model="loginForm.username" placeholder="用户名" required />
          <input v-model="loginForm.password" type="password" placeholder="密码" required />
          <button type="submit">登录</button>
        </form>
        <h2>注册</h2>
        <form @submit.prevent="register">
          <input v-model="registerForm.username" placeholder="用户名" required />
          <input v-model="registerForm.password" type="password" placeholder="密码" required />
          <button type="submit">注册</button>
        </form>
      </div>

      <div v-if="isLoggedIn">
        <h2>记录收支</h2>
        <form @submit.prevent="addRecord">
          <input v-model.number="recordForm.amount" type="number" placeholder="金额" required />
          <input v-model="recordForm.category" placeholder="类别" required />
          <select v-model="recordForm.type" required>
            <option value="income">收入</option>
            <option value="expense">支出</option>
          </select>
          <input v-model="recordForm.note" placeholder="备注（可选）" />
          <button type="submit">添加记录</button>
        </form>

        <h2>收支明细</h2>
        <ul>
          <li v-for="record in records" :key="record.id">
            {{ record.date }} - {{ record.category }} - {{ record.amount }} - {{ record.type }} - {{ record.note }}
            <button @click="deleteRecord(record.id)">删除</button>
            <button @click="editRecord(record)">编辑</button>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import {ref} from 'vue';
import axios from 'axios';

axios.defaults.baseURL = 'http://localhost:5000';
axios.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = token;
  }
  return config;
}, (error) => Promise.reject(error));

// 响应式数据
const isLoggedIn = ref(false);
const registerForm = ref({username: '', password: ''});
const loginForm = ref({username: '', password: ''});
const recordForm = ref({amount: null, category: '', type: 'income', note: '',timeStamp:1735638043000});
const records = ref([]);

// 方法
const register = async () => {
  try {
    await axios.post('/register', registerForm.value);
    alert('注册成功，请登录！');
  } catch (error) {
    alert(error.response?.data?.error || '注册失败');
  }
};

const login = async () => {
  try {
    const response = await axios.post('/login', loginForm.value);
    localStorage.setItem('token', response.data.token);
    isLoggedIn.value = true;
    fetchRecords();
  } catch (error) {
    alert(error.response?.data?.error || '登录失败');
  }
};

const addRecord = async () => {
  try {
    await axios.post('/records', recordForm.value);
    alert('记录添加成功！');
    fetchRecords();
  } catch (error) {
    alert(error.response?.data?.error || '添加记录失败');
  }
};

const fetchRecords = async () => {
  try {
    const response = await axios.get('/records');
    records.value = response.data;
    console.log(records.value);
  } catch (error) {
    alert('获取记录失败');
  }
};

const deleteRecord = async (recordId) => {
  try {
    await axios.delete(`/records/${recordId}`);
    alert('记录删除成功！');
    fetchRecords();
  } catch (error) {
    alert('删除记录失败');
  }
};

const editRecord = async (record) => {
  const updatedRecord = {...record, note: prompt('修改备注：', record.note)};
  try {
    await axios.put(`/records/${record.id}`, updatedRecord);
    alert('记录更新成功！');
    fetchRecords();
  } catch (error) {
    alert('更新记录失败');
  }
};
</script>

<style scoped>
#app {
  font-family: Arial, sans-serif;
  margin: 20px;
}

input, button, select {
  margin: 5px;
}
</style>
