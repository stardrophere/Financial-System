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
          <button type="submit">添加记录</button>
        </form>

        <h2>收支明细</h2>
        <ul>
          <li v-for="record in records" :key="record.id">
            {{ record.date }} - {{ record.category }} - {{ record.amount }} - {{ record.type }}
          </li>
        </ul>

        <h2>账单汇总</h2>
        <p>总收入: {{ summary.total_income }}</p>
        <p>总支出: {{ summary.total_expense }}</p>
        <p>结余: {{ summary.balance }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import axios from "axios";

// axios.defaults.baseURL = "http://localhost:5000";
axios.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = token;
  }
  return config;
}, (error) => Promise.reject(error));

const isLoggedIn = ref(false);
const loginForm = ref({ username: "", password: "" });
const registerForm = ref({ username: "", password: "" });
const recordForm = ref({ amount: null, category: "", type: "income" });
const records = ref([]);
const summary = ref({ total_income: 0, total_expense: 0, balance: 0 });

const register = async () => {
  try {
    await axios.post("/register", registerForm.value);
    alert("注册成功，请登录！");
  } catch (error) {
    alert(error.response?.data?.error || "注册失败");
  }
};

const login = async () => {
  try {
    const response = await axios.post("/login", loginForm.value);
    const token = response.data.token;
    localStorage.setItem("token", token);
    isLoggedIn.value = true;
    // fetchRecords();
    // fetchSummary();
  } catch (error) {
    alert(error.response?.data?.error || "登录失败");
    console.log(error.response.data.error);
  }
};

const addRecord = async () => {
  try {
    await axios.post("/records", recordForm.value);
    alert("记录添加成功！");
    fetchRecords();
    fetchSummary();
  } catch (error) {
    alert(error.response?.data?.error || "添加记录失败");
  }
};

const fetchRecords = async () => {
  try {
    const response = await axios.get("/records");
    records.value = response.data;
  } catch (error) {
    alert("获取记录失败");
  }
};

const fetchSummary = async () => {
  try {
    const response = await axios.get("/summary");
    summary.value = response.data;
  } catch (error) {
    alert("获取汇总失败");
  }
};

const logout = () => {
  localStorage.removeItem("token");
  isLoggedIn.value = false;
  alert("已登出");
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
