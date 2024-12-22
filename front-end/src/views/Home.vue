<template>
  <div class="login-container">
    <el-card class="login-card" shadow="hover">
      <h2 class="login-title" >登录</h2>

      <el-form :model="loginForm" :rules="rules" ref="loginFormRef" label-width="10px" status-icon label-position="top" size="large">
        <!-- 用户名输入框 -->
        <el-form-item label="用户名" prop="username">
          <el-input v-model="loginForm.username" placeholder="请输入用户名" />
        </el-form-item>

        <!-- 密码输入框 -->
        <el-form-item label="密码" prop="password">
          <el-input v-model="loginForm.password" placeholder="请输入密码" type="password" />
        </el-form-item>

      </el-form>
      <!-- 登录按钮 -->
      <div class="button-container">
        <el-button type="primary" @click="onSubmit" class="button-type" size="large">登录</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue';
import { ElMessage } from 'element-plus';

// 登录表单数据
const loginForm = reactive({
  username: '',
  password: '',
});

// 表单验证规则
const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
  ],
};

const loginFormRef = ref(null);

// 提交表单
const onSubmit = () => {
  loginFormRef.value.validate((valid) => {
    if (valid) {
      ElMessage.success('登录成功！');
    } else {
      ElMessage.error('请填写完整的登录信息');
    }
  });
};

</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f5f5f5;

}

.login-card {
  width: 400px;
  padding: 20px;
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

.button-type{
  width: 100%;
}
</style>
