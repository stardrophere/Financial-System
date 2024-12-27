<script setup>
import TopBar from "@/components/topBar.vue";
import RenderCharts from "@/components/RenderCharts.vue";
</script>

<template>
  <div class="back-ground">
    <TopBar class="top-bar"/>

    <div class="page-container">
      <RenderCharts/>
    </div>

  </div>
</template>

<style scoped>
/* 固定顶部栏 */
.top-bar {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  z-index: 1000; /* 确保顶部栏在最上层 */

}

.back-ground {
  height: 100vh;
  width: 100%;
  background: linear-gradient(200deg, #f3e7e9, #cddffa);
}

.page-container {
  display: flex;
  flex-direction: column;
  align-items: center; /* 水平居中 */
  padding: 20px; /* 可选：添加内边距 */
  padding-top: 75px; /* 根据顶部栏高度调整 */
  /* 可选：添加背景样式 */
  background: linear-gradient(to right, #e0eafc, #cfdef3);
  min-height: 92vh;

}
</style>