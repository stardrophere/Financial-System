<template>
  <!-- 创建一个表单，model 绑定到 form，label-width 为自动，最大宽度 600px -->
  <el-form :model="form" label-width="auto" style="max-width: 600px" label-position="top" status-icon>

    <!-- 活动时间选择 -->
    <el-form-item label="时间">
      <!-- 时间选择框布局 -->
      <el-date-picker
          v-model="form.date1"
          type="datetime"
          placeholder="Select date and time"
      />


    </el-form-item>

    <!-- 活动名称输入框 -->
    <el-form-item label="金额">
      <!-- v-model 双向绑定 form.name 数据，用于保存活动名称 -->
      <el-input v-model="form.name"/>
    </el-form-item>


    <!-- 即时配送选择框 -->
    <el-form-item label="Instant delivery">
      <!-- 开关控件，v-model 双向绑定 form.delivery 数据 -->
      <el-switch v-model="form.delivery"/>
    </el-form-item>

    <!-- 活动类型多选框 -->
    <el-form-item label="Activity type">
      <!-- 多选框组，v-model 双向绑定 form.type 数组 -->
      <el-checkbox-group v-model="form.type">
        <!-- 活动类型选项：在线活动 -->
        <el-checkbox value="Online activities" name="type">
          Online activities
        </el-checkbox>
        <!-- 活动类型选项：促销活动 -->
        <el-checkbox value="Promotion activities" name="type">
          Promotion activities
        </el-checkbox>
        <!-- 活动类型选项：线下活动 -->
        <el-checkbox value="Offline activities" name="type">
          Offline activities
        </el-checkbox>
        <!-- 活动类型选项：简单品牌曝光 -->
        <el-checkbox value="Simple brand exposure" name="type">
          Simple brand exposure
        </el-checkbox>
      </el-checkbox-group>
    </el-form-item>

    <!-- 资源类型单选框 -->
    <el-form-item label="Resources">
      <!-- 单选框组，v-model 双向绑定 form.resource 数据 -->
      <el-radio-group v-model="form.resource">
        <!-- 资源选项：赞助商 -->
        <el-radio value="Sponsor">Sponsor</el-radio>
        <!-- 资源选项：场地 -->
        <el-radio value="Venue">Venue</el-radio>
      </el-radio-group>
    </el-form-item>

    <!-- 活动描述文本框 -->
    <el-form-item label="Activity form">
      <!-- 文本框，v-model 双向绑定 form.desc 数据，type 为 textarea -->
      <el-input v-model="form.desc" type="textarea"/>
    </el-form-item>

    <!-- 提交按钮与取消按钮 -->
    <el-form-item>
      <!-- 提交按钮，点击时调用 onSubmit 方法 -->
      <el-button type="primary" @click="onSubmit">Create</el-button>
      <!-- 取消按钮 -->
      <el-button>Cancel</el-button>
    </el-form-item>
  </el-form>
</template>

<script lang="ts" setup>
import {reactive} from 'vue'

// 创建表单的响应式数据对象 `form`，用于绑定表单项的值
const form = reactive({
  name: '',         // 活动名称
  region: '',       // 活动区域
  date1: '',        // 活动日期
  date2: '',        // 活动时间
  delivery: false,  // 是否即时配送
  type: [],         // 活动类型，数组存储多个选择
  resource: '',     // 资源类型（如赞助商或场地）
  desc: '',         // 活动描述
})

// 提交表单的方法
const onSubmit = () => {
  if (form.date1) {
    // 将 Date 对象转换为时间戳
    const timestamp = new Date(form.date1).getTime();
    console.log("Selected timestamp:", timestamp);
  } else {
    console.log("No date selected");
  }
};
</script>
