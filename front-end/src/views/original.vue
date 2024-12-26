<template>
  <el-button @click="addRecord" type="primary" round>添加记录</el-button>
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


    <!-- 第二列：显示名称 -->
    <el-table-column label="类别" width="180" align="center">
      <!-- 自定义列内容，通过插槽模板实现 -->
      <template #default="scope">
        <div style="display: flex; justify-content: center; align-items: center; width: 100%;">
          <el-button round
                     :style="{ backgroundColor: categoryColors[scope.row.type][scope.row.category], color: '#ffffff' }">
            {{ scope.row.category }}
          </el-button>
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
            <img src="@/assets/income.svg" alt="Income Icon" style="width: 28px; height: 28px;"/>
          </el-button>
          <el-button type="info" circle size="large" v-else>
            <img src="@/assets/expense.svg" alt="Income Icon" style="width: 28px; height: 28px;"/>
          </el-button>
        </div>
      </template>
    </el-table-column>

    <el-table-column label="备注" width="300" align="center">
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

  <!--  表格挂载-->
  <el-dialog v-model="formVisible" :title="formTitle" width="500">
    <RecordChange ref="formRef" @cancel="formVisible=false" @success="handleFormSuccess"/>
  </el-dialog>
</template>

<script setup>
import {ElMessage} from "element-plus";
import {ref, nextTick} from "vue";
import axios from "axios";
import {categoryColors} from "@/config/colors.js"; //类别颜色库
import RecordChange from "@/components/RecordChange.vue";

const formVisible = ref(false);
const formTitle = ref("添加记录")
const formRef = ref(null);
const currentEditRow = ref(null); // 存储当前编辑的行数据

// 请求拦截器：在每个请求中添加Authorization头
axios.interceptors.request.use(
    (config) => {
      const token = localStorage.getItem('token');
      if (token) {
        config.headers.Authorization = token;
      }
      return config;
    },
    (error) => {
      // 请求错误时的处理
      return Promise.reject(error);
    }
);

// 响应拦截器：处理401错误并跳转到登录页
axios.interceptors.response.use(
    (response) => {
      // 如果响应成功，直接返回响应数据
      return response;
    },
    (error) => {
      if (error.response && error.response.status === 401) {
        WarningPop("登陆过期,将自动跳转至登录页面");
        setTimeout(() => window.location.href = '/loginRegister', 1500)
      }
      // 其他错误继续返回
      return Promise.reject(error);
    }
);
// 编辑操作的处理函数
// 参数：
// - index: 行的索引
// - row: 当前行的数据对象
// 编辑操作的处理函数
const handleEdit = (index, row) => {
  formTitle.value = "编辑记录";
  currentEditRow.value = {...row}; // 深拷贝当前行数据
  formVisible.value = true;

  // 使用 nextTick 确保子组件已挂载
  nextTick(() => {
    if (formRef.value && formRef.value.initForm) {
      formRef.value.initForm(false, currentEditRow.value);
    } else {
      console.error("子组件的方法未找到或子组件未挂载");
    }
  });
};

const addRecord = () => {
  formTitle.value = "添加记录";
  formVisible.value = true;

  // 使用 nextTick 确保子组件已挂载
  nextTick(() => {
    if (formRef.value && formRef.value.initForm) {
      formRef.value.initForm(true, {});
    } else {
      console.error("子组件的方法未找到或子组件未挂载");
    }
  });
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
    console.log("收取", tableData.value);
  } catch (error) {
    ErrorPop("更新失败")
  }
};


//日期排序
const sortByDate = (a, b) => {
  return new Date(a.date).getTime() - new Date(b.date).getTime();
};

// 弹窗方法
// 错误弹窗
const ErrorPop = (info, time = 3000) => {
  ElMessage({
    showClose: true,
    message: info,
    type: 'error',
    duration: time
  });
};

// 成功弹窗
const SuccessPop = (info, time = 3000) => {
  ElMessage({
    showClose: true,
    message: info,
    type: 'success',
    duration: time
  });
};

// 警告弹窗
const WarningPop = (info, time = 3000) => {
  ElMessage({
    showClose: true,
    message: info,
    type: 'warning',
    duration: time
  });
};

const handleFormSuccess = () => {
  formVisible.value = false;
  fetchRecords();
}
</script>

<style scoped>
.table {
  width: 100%;
  font-size: 16px;
}
</style>