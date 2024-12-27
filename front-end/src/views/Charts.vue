<script setup>
import TopBar from "@/components/topBar.vue";
import RenderCharts from "@/components/RenderCharts.vue";
</script>

<template>
  <div class="back-ground">
    <TopBar/>
    <RenderCharts style="margin-top: 50px"/>
  </div>
</template>

<style scoped>
.back-ground {
  height: 100vh;
  width: 100%;
  background: linear-gradient(to right, #e0eafc, #cfdef3);
}
</style>