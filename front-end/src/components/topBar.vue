<template>
  <el-menu
      :default-active="$route.path"
      class="el-menu-demo"
      mode="horizontal"
      :ellipsis="false"
      @select="handleSelect"
      background-color="#545c64"
      text-color="#fff"
      active-text-color="#ffd04b"
      router
  >
    <!-- logo部分 -->
    <el-menu-item>
      <el-dropdown @command="handleCommand" trigger="click">
        <span class="el-dropdown-link">
          <img
              style="width: 50px"
              src="@/assets/logo.webp"
              alt="logo"
              class="icon"
          />
        </span>
        <template #dropdown>
          <el-dropdown-item command="logout">注销登录</el-dropdown-item>
        </template>
      </el-dropdown>
    </el-menu-item>

    <!-- 其他菜单项 -->
    <el-menu-item index="/records" @click="navigateTo('/records')">收支记录</el-menu-item>
    <el-menu-item index="/charts" @click="navigateTo('/charts')">图表</el-menu-item>
    <el-menu-item index="/reports" @click="navigateTo('/reports')">报告</el-menu-item>
  </el-menu>
</template>

<script lang="ts" setup>
import {ref} from 'vue'
import {useRouter} from 'vue-router'
import {ElMessage} from "element-plus";  // 导入 vue-router 用于跳转


// 获取 router 实例
const router = useRouter()

// 处理菜单项选择
const handleSelect = (key: string, keyPath: string[]) => {
  // console.log(key, keyPath)
}

// 处理下拉菜单项点击
const handleCommand = (command: string) => {
  if (command === 'logout') {
    // 在这里处理注销登录逻辑
    // 例如，清除用户认证信息、token 等
    console.log('用户注销登录');
    localStorage.removeItem('token');


    // 显示成功消息
    ElMessage.success("注销成功");

    // 跳转到登录页面
    navigateTo("/loginRegister")
  }
}

// 跳转到不同的路由
const navigateTo = (path: string) => {
  router.push(path)  // 使用 vue-router 的 push 方法跳转到对应的路由路径
}
</script>

<style scoped>
.icon {
  border-radius: 50%;
}
</style>
