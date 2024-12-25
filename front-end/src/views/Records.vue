<template>
  <!-- 创建一个表格组件，使用 Element Plus 的 el-table -->
  <el-table :data="tableData"
            size="large"
            class="table"
  >


    <!-- 第一列：显示日期 -->
    <el-table-column label="时间" width="180" sortable :sort-method="sortByDate" align="center">
      <!-- 自定义列内容，通过插槽模板实现 -->
      <template #default="scope">
        <!-- 显示日期的行，包含图标和日期 -->
        <div style="display: flex; justify-content: center; align-items: center; width: 100%;">
          <span>
<!--            <el-icon style="margin-right: 5px">-->
            <!--            <timer/>-->
            <!--          </el-icon>-->
              {{ scope.row.date }} <!-- 显示日期 -->
          </span>
        </div>
      </template>
    </el-table-column>

    <!--    &lt;!&ndash; 第二列：显示名称 &ndash;&gt;-->
    <!--    <el-table-column label="类别" width="180">-->
    <!--      &lt;!&ndash; 自定义列内容，通过插槽模板实现 &ndash;&gt;-->
    <!--      <template #default="scope">-->
    <!--        &lt;!&ndash; 使用弹出框（popover）在悬停时显示详细信息 &ndash;&gt;-->
    <!--        <el-popover effect="light" trigger="hover" placement="top" width="auto">-->
    <!--          &lt;!&ndash; 弹出框的内容 &ndash;&gt;-->
    <!--          <template #default>-->
    <!--            <div>name: {{ scope.row.name }}</div> &lt;!&ndash; 显示名称 &ndash;&gt;-->
    <!--            <div>address: {{ scope.row.address }}</div> &lt;!&ndash; 显示地址 &ndash;&gt;-->
    <!--          </template>-->
    <!--          &lt;!&ndash; 触发弹出框的参考元素 &ndash;&gt;-->
    <!--          <template #reference>-->
    <!--            <el-tag>{{ scope.row.name }}</el-tag> &lt;!&ndash; 显示名称为标签形式 &ndash;&gt;-->
    <!--          </template>-->
    <!--        </el-popover>-->
    <!--      </template>-->
    <!--    </el-table-column>-->

    <!-- 第二列：显示名称 -->
    <el-table-column label="类别" width="180" align="center">
      <!-- 自定义列内容，通过插槽模板实现 -->
      <template #default="scope">
        <div style="display: flex; justify-content: center; align-items: center; width: 100%;">
          <el-button round style="background-color: #ae7fb6; color: #ffffff">{{ scope.row.category }}</el-button>
        </div>
      </template>
    </el-table-column>


    <el-table-column label="金额" align="center" width="180">
      <!-- 自定义列内容，通过插槽模板实现 -->
      <template #default="scope">
        <div style="display: flex; justify-content: center; align-items: center; width: 100%;">
          {{ scope.row.amount }}
        </div>
      </template>
    </el-table-column>

    <el-table-column label="类型" width="180" align="center">
      <!-- 自定义列内容，通过插槽模板实现 -->
      <template #default="scope">
        <div style="display: flex; justify-content: center; align-items: center; width: 100%;">
          <el-button type="info" circle size="large" v-if="scope.row.type==='income'">
            <img src="@/assets/income.svg" alt="Income Icon" style="width: 30px; height: 30px;"/>
          </el-button>
          <el-button type="info" circle size="large" v-else>
            <img src="@/assets/expense.svg" alt="Income Icon" style="width: 30px; height: 30px;"/>
          </el-button>
        </div>
      </template>
    </el-table-column>

    <el-table-column label="备注" width="180" align="center">
      <!-- 自定义列内容，通过插槽模板实现 -->
      <template #default="scope">
        <div style="display: flex; justify-content: center; align-items: center; width: 100%;">
          {{ scope.row.note }}
        </div>
      </template>
    </el-table-column>


    <!-- 操作列 -->
    <el-table-column label="" fixed="right" align="center">
      <!-- 自定义列内容，通过插槽模板实现 -->
      <template #default="scope">
        <!-- 编辑按钮 -->
        <el-button size="default" @click="handleEdit(scope.$index, scope.row)">
          编辑 <!-- 按钮文字为 "Edit" -->
        </el-button>
        <!-- 删除按钮 -->
        <!-- 设置按钮类型为 "danger"，用于警示性操作 -->
        <el-button size="default" type="danger" @click="handleDelete(scope.$index, scope.row)">
          删除 <!-- 按钮文字为 "Delete" -->
        </el-button>
      </template>
    </el-table-column>
  </el-table>
  <button @click="fetchRecords">)))<<<</button>
</template>

<script setup>
import {ElMessage} from "element-plus";
import {ref} from "vue";
import axios from "axios";


axios.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = token;
  }
  return config;
}, (error) => Promise.reject(error));
// 编辑操作的处理函数
// 参数：
// - index: 行的索引
// - row: 当前行的数据对象
const handleEdit = (index, row) => {
  console.log(index, row) // 打印索引和当前行的数据
}

// 删除操作的处理函数
// 参数：
// - index: 行的索引
// - row: 当前行的数据对象
const handleDelete = (index, row) => {
  console.log("删除", index, row.id) // 打印索引和当前行的数据
  deleteRecord(row.id);
  tableData.value.splice(index, 1);
}

const deleteRecord = async (recordId) => {
  try {
    await axios.delete(`/records/${recordId}`);
    SuccessPop('记录删除成功！');
  } catch (error) {
    ErrorPop('删除记录失败');
  }
};

// 表格数据
const tableData = ref([])

//更新表格数据
const fetchRecords = async () => {
  try {
    const response = await axios.get('/records');
    tableData.value = response.data;
    console.log(tableData.value);
  } catch (error) {
    ErrorPop("更新失败")
  }
};


//日期排序
const sortByDate = (a, b) => {
  return new Date(a.date).getTime() - new Date(b.date).getTime();
};

//错误弹窗
const ErrorPop = (info, time = 3000) => {
  ElMessage({
    showClose: true,
    message: info,
    type: 'error',
    duration: time
  })
}

//成功弹窗
const SuccessPop = (info, time = 3000) => {
  ElMessage({
    showClose: true,
    message: info,
    type: 'success',
    duration: time
  })
}
</script>

<style scoped>
.table {
  width: 100%;
  font-size: 16px;
}
</style>