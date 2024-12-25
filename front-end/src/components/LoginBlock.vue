<template>
  <div class="login-container">
    <el-card class="login-card" shadow="hover">

      <el-form :model="loginForm" :rules="rules" ref="loginFormRef" label-width="10px" label-position="top"
               size="large">
        <!-- 用户名输入框 -->
        <el-form-item label="用户名" prop="username">
          <el-input v-model="loginForm.username" placeholder="请输入用户名"/>
        </el-form-item>

        <!-- 密码输入框 -->
        <el-form-item label="密码" prop="password">
          <el-input v-model="loginForm.password" placeholder="请输入密码" type="password"/>
        </el-form-item>

      </el-form>
      <!-- 登录按钮 -->
      <div class="button-container">
        <el-button type="primary" @click="onSubmit" class="button_type" size="large">登录</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import {reactive, ref} from 'vue';
import {ElMessage} from 'element-plus';
import router from "@/router/index.js";
import axios from "axios";

// 登录表单数据
const loginForm = reactive({
  username: '',
  password: '',
});

// 表单验证规则
const rules = {
  username: [
    {required: true, message: '请输入用户名', trigger: 'blur'},
  ],
  password: [
    {required: true, message: '请输入密码', trigger: 'blur'},
  ],
};

const loginFormRef = ref(null);

// 提交表单
const onSubmit = () => {
  loginFormRef.value.validate((valid) => {
    if (valid) {
      loginIn();
    } else {
      ElMessage.error('请填写完整的登录信息');
    }
  });
};


//登录
const loginIn = async () => {
  try {
    const response = await axios.post("/login", loginForm);
    const token = response.data.token;
    localStorage.setItem("token", token);
    ElMessage.success("登录成功");
    await navigateTo("/records");
    // setTimeout(()=>navigateTo("/records"),500);

  } catch (error) {
    const msg = error.response.data.error
    console.log(msg)
    ElMessage.error(msg);


  }
};


const navigateTo = (path) => {
  router.push(path)  // 使用 vue-router 的 push 方法跳转到对应的路由路径
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;


}


.login-card {

  padding: 5px;
  border-radius: 12px;
}

.login-title {
  margin-bottom: 20px;
  font-size: 24px;
  color: #333;
  text-align: center;
}

.button-container {
  display: flex;
  justify-content: center;
  gap: 10px;
  width: 100%;
}

.button_type {
  width: 100%;
}
</style>
