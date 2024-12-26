<template>
  <TopBar class="top-bar"/>
  <div class="page-container">
    <RecordTable/>
  </div>
</template>

<script setup>
import RecordTable from "@/components/RecordTable.vue";
import TopBar from "@/components/TopBar.vue";
</script>

<style scoped>
/* 固定顶部栏 */
.top-bar {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  z-index: 1000; /* 确保顶部栏在最上层 */

}

/* 页面内容容器 */
.page-container {
  display: flex;
  flex-direction: column;
  align-items: center; /* 水平居中 */
  padding: 20px; /* 可选：添加内边距 */
  padding-top: 80px; /* 根据顶部栏高度调整 */
  /* 可选：添加背景样式 */
  background: linear-gradient(to right, #e0eafc, #cfdef3);
  min-height: 100vh;
}

/* 响应式调整（可选） */
@media (max-width: 768px) {
  .page-container {
    padding-top: 60px; /* 根据顶部栏在小屏幕上的高度调整 */
  }
}
</style>
