<template>
  <div class="register-container">
    <el-card class="register-card" shadow="hover">

      <el-form :model="registerForm" :rules="rules" ref="registerFormRef" label-width="10px"  label-position="top" size="large">
        <!-- 用户名输入框 -->
        <el-form-item label="用户名" prop="username">
          <el-input v-model="registerForm.username" placeholder="请输入用户名" />
        </el-form-item>

        <!-- 密码输入框 -->
        <el-form-item label="密码" prop="password">
          <el-input v-model="registerForm.password" placeholder="请输入密码" type="password" />
        </el-form-item>

      </el-form>
      <!-- 注册按钮 -->
      <div class="button-container">
        <el-button type="primary" @click="onSubmit" class="button-type" size="large">注册</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue';
import { ElMessage } from 'element-plus';

// 注册表单数据
const registerForm = reactive({
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

const registerFormRef = ref(null);

// 提交表单
const onSubmit = () => {
  registerFormRef.value.validate((valid) => {
    if (valid) {
      ElMessage.success('注册成功！');
    } else {
      ElMessage.error('请填写完整的注册信息');
    }
  });
};

</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;


}


.register-card {

  padding: 5px;
  border-radius: 12px;
}

.register-title {
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
