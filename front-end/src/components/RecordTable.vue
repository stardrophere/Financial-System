<template>
  <div class="table-wrapper">
    <!-- 操作区域，使用 Flex 布局 -->
    <div class="operations">
      <!-- 左侧操作按钮 -->
      <div class="left-buttons">
        <el-button @click="addRecord" type="primary" round>添加记录</el-button>
        <el-button
            @click="downloadSelectedExcel"
            type="success"
            round
            style="margin-left: 10px;"
            :loading="isDownloadingSelected"
        >
          下载选中
        </el-button>
        <el-button
            @click="downloadExcel"
            type="info"
            round
            style="margin-left: 10px;"
            :loading="isDownloadingAll"
        >
          下载全部
        </el-button>
        <!-- 上传按钮 -->
        <el-upload
            class="upload-button"
            action=""
            :show-upload-list="false"
            :before-upload="handleBeforeUpload"
        >
          <el-button
              type="warning"
              round
              style="margin-left: 10px;margin-top: 10px"
              :loading="isUploading"
          >
            上传 Excel
          </el-button>
        </el-upload>
      </div>

      <!-- 右侧搜索输入框 -->
      <div class="right-search">
        <el-input
            placeholder="搜索备注"
            v-model="noteSearch"
            clearable
            style="width: 300px;"
            @clear="handleNoteSearch"
            @input="handleNoteSearch"
            size="large"
        >
          <template #prefix>
            <el-icon>
              <Search/>
            </el-icon>
          </template>
        </el-input>
      </div>
    </div>

    <!-- 表格容器，添加圆角和阴影，并设置固定高度 -->
    <div class="table-container">
      <!-- 创建一个表格组件，使用 Element Plus 的 el-table -->
      <el-table
          :data="filteredTableData"
          size="large"
          class="table"
          style="width: 100%;"
          @selection-change="handleSelectionChange"
          ref="tableRef"
          max-height="1080px"

      >
        <!-- 多选列 -->
        <el-table-column type="selection" width="55"></el-table-column>

        <!-- 第一列：显示日期 -->
        <el-table-column label="时间" width="180" sortable :sort-method="sortByDate" align="center">
          <template #default="scope">
            <div class="table-cell">
              <span>{{ scope.row.date }}</span>
            </div>
          </template>
        </el-table-column>

        <!-- 第二列：显示类别 -->
        <el-table-column
            label="类别"
            width="180"
            align="center"
            :filters="categoryFilterOptions"
            :filter-method="filterCategory"
            filter-placement="bottom-start"
        >
          <template #default="scope">
            <div class="table-cell">
              <el-button round
                         :style="{ backgroundColor: categoryColors[scope.row.type][scope.row.category], color: '#ffffff' }">
                {{ scope.row.category }}
              </el-button>
            </div>
          </template>
        </el-table-column>

        <!-- 第三列：显示金额 -->
        <el-table-column
            label="金额"
            align="center"
            width="180"
            sortable
            :sort-method="sortByAmount"
        >
          <template #default="scope">
            <div class="table-cell">
              {{ scope.row.amount }}
            </div>
          </template>
        </el-table-column>

        <!-- 第四列：显示类型 -->
        <el-table-column
            label="类型"
            width="180"
            align="center"
            :filters="typeFilterOptions"
            :filter-method="filterType"
            filter-placement="bottom-start"
        >
          <template #default="scope">
            <div class="table-cell">
              <el-button type="info" circle size="large" v-if="scope.row.type==='income'">
                <img src="@/assets/income.svg" alt="Income Icon" style="width: 28px; height: 28px;"/>
              </el-button>
              <el-button type="info" circle size="large" v-else>
                <img src="@/assets/expense.svg" alt="Expense Icon" style="width: 28px; height: 28px;"/>
              </el-button>
            </div>
          </template>
        </el-table-column>

        <!-- 第五列：显示备注 -->
        <el-table-column label="备注" width="300" align="center">
          <template #default="scope">
            <div class="table-cell">
              {{ scope.row.note }}
            </div>
          </template>
        </el-table-column>

        <!-- 操作列 -->
        <el-table-column label="" fixed="right" align="center" width="200">
          <template #default="scope">
            <el-button size="default" @click="handleEdit(scope.$index, scope.row)">
              编辑
            </el-button>
            <el-button size="default" type="danger" @click="handleDelete(scope.$index, scope.row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 表格挂载-->
    <el-dialog v-model="formVisible" :title="formTitle" width="500">
      <RecordChange ref="formRef" @cancel="formVisible=false" @success="handleFormSuccess"/>
    </el-dialog>
  </div>
</template>

<script setup>
import {ElMessage} from "element-plus";
import {ref, computed, nextTick} from "vue";
import axios from "axios";
import {categoryColors} from "@/config/colors.js"; // 类别颜色库
import RecordChange from "@/components/RecordChange.vue";
import {Search} from "@element-plus/icons-vue";
import * as XLSX from 'xlsx'; // 导入xlsx
import {saveAs} from 'file-saver'; // 导入file-saver

const formVisible = ref(false);
const formTitle = ref("添加记录");
const formRef = ref(null);
const currentEditRow = ref(null); // 存储当前编辑的行数据

// 搜索备注的关键字
const noteSearch = ref("");

// 存储选中的行数据
const selectedRows = ref([]);

// 下载按钮的加载状态
const isDownloadingSelected = ref(false);
const isDownloadingAll = ref(false);

// 上传按钮的加载状态
const isUploading = ref(false);


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

// 添加记录的处理函数
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
};

// 删除操作的处理函数
const handleDelete = (index, row) => {
  console.log("删除", index, row.id); // 打印索引和当前行的数据
  deleteRecord(row.id);
  tableData.value.splice(index, 1);
};

// 删除记录的 API 调用
const deleteRecord = async (recordId) => {
  try {
    await axios.delete(`/records/${recordId}`);
    SuccessPop('记录删除成功！');
  } catch (error) {
    ErrorPop('删除记录失败');
  }
};

// 表格数据
const tableData = ref([]);

// 获取记录的 API 调用
const fetchRecords = async () => {
  try {
    const response = await axios.get('/records');
    tableData.value = response.data;
    console.log("获取到的记录", tableData.value);
  } catch (error) {
    ErrorPop("更新失败");
  }
};

// 初始获取记录
fetchRecords();

// 日期排序方法
const sortByDate = (a, b) => {
  return new Date(a.date).getTime() - new Date(b.date).getTime();
};

// 金额排序方法
const sortByAmount = (a, b) => {
  return a.amount - b.amount;
};

// 类别筛选选项
const categoryFilterOptions = computed(() => {
  const categories = new Set();
  tableData.value.forEach(record => {
    categories.add(record.category);
  });
  return Array.from(categories).map(category => ({text: category, value: category}));
});

// 类型筛选选项
const typeFilterOptions = [
  {text: '收入', value: 'income'},
  {text: '支出', value: 'expense'}
];

// 类别筛选方法
const filterCategory = (value, row) => {
  return row.category === value;
};

// 类型筛选方法
const filterType = (value, row) => {
  return row.type === value;
};

// 备注搜索处理函数
const handleNoteSearch = () => {
  // 由于使用了计算属性，直接触发计算即可
};

// 计算过滤后的表格数据
const filteredTableData = computed(() => {
  let data = tableData.value;

  // 由于 el-table 内部已经处理了过滤，这里只需要处理备注搜索
  if (noteSearch.value) {
    const keyword = noteSearch.value.toLowerCase();
    data = data.filter(record => record.note.toLowerCase().includes(keyword));
  }

  return data;
});

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

// 处理表单成功后的逻辑
const handleFormSuccess = () => {
  formVisible.value = false;
  fetchRecords();
};

// 处理表格选择项变化
const handleSelectionChange = (val) => {
  selectedRows.value = val;
  console.log("选中的行：", selectedRows.value);
};

// 下载选中行的Excel文件
const downloadSelectedExcel = async () => {
  if (selectedRows.value.length === 0) {
    WarningPop('请先选择要下载的记录！');
    return;
  }

  isDownloadingSelected.value = true;

  try {
    // 动态获取表格列标题
    const columns = [
      {label: "时间", prop: "date"},
      {label: "类别", prop: "category"},
      {label: "金额", prop: "amount"},
      {label: "类型", prop: "type"},
      {label: "备注", prop: "note"}
    ];

    // 准备Excel数据
    const worksheetData = selectedRows.value.map(record => {
      return {
        [columns[0].label]: record.date,
        [columns[1].label]: record.category,
        [columns[2].label]: record.amount,
        [columns[3].label]: record.type === 'income' ? '收入' : '支出',
        [columns[4].label]: record.note
      };
    });

    // 创建工作表
    const worksheet = XLSX.utils.json_to_sheet(worksheetData);

    // 创建工作簿并添加工作表
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, "选中记录");

    // 生成 Excel 文件的二进制数据
    const wbout = XLSX.write(workbook, {bookType: 'xlsx', type: 'array'});

    // 使用file-saver保存文件
    const blob = new Blob([wbout], {type: 'application/octet-stream'});
    saveAs(blob, `选中记录_${getCurrentDate()}.xlsx`);

    SuccessPop('选中的Excel文件已生成并下载！');
  } catch (error) {
    ErrorPop('下载选中记录失败，请稍后重试。');
  } finally {
    isDownloadingSelected.value = false;
  }
};

// 下载全部筛选后的数据的Excel文件
const downloadExcel = async () => {
  if (filteredTableData.value.length === 0) {
    WarningPop('当前没有数据可以下载！');
    return;
  }

  isDownloadingAll.value = true;

  try {
    // 动态获取表格列标题
    const columns = [
      {label: "时间", prop: "date"},
      {label: "类别", prop: "category"},
      {label: "金额", prop: "amount"},
      {label: "类型", prop: "type"},
      {label: "备注", prop: "note"}
    ];

    // 准备Excel数据
    const worksheetData = filteredTableData.value.map(record => {
      return {
        [columns[0].label]: record.date,
        [columns[1].label]: record.category,
        [columns[2].label]: record.amount,
        [columns[3].label]: record.type === 'income' ? '收入' : '支出',
        [columns[4].label]: record.note
      };
    });

    // 创建工作表
    const worksheet = XLSX.utils.json_to_sheet(worksheetData);

    // 创建工作簿并添加工作表
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, "全部记录");

    // 生成 Excel 文件的二进制数据
    const wbout = XLSX.write(workbook, {bookType: 'xlsx', type: 'array'});

    // 使用file-saver保存文件
    const blob = new Blob([wbout], {type: 'application/octet-stream'});
    saveAs(blob, `全部记录_${getCurrentDate()}.xlsx`);

    SuccessPop('全部的Excel文件已生成并下载！');
  } catch (error) {
    ErrorPop('下载全部记录失败，请稍后重试。');
  } finally {
    isDownloadingAll.value = false;
  }
};

// 获取当前日期，格式为 YYYY-MM-DD
const getCurrentDate = () => {
  const date = new Date();
  const year = date.getFullYear();
  const month = (`0${date.getMonth() + 1}`).slice(-2);
  const day = (`0${date.getDate()}`).slice(-2);
  return `${year}-${month}-${day}`;
};

// 上传按钮的处理逻辑

// 处理上传前的文件选择
const handleBeforeUpload = (file) => {
  // 检查文件类型是否为Excel
  const isExcel = file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' ||
      file.type === 'application/vnd.ms-excel';
  if (!isExcel) {
    ErrorPop('只能上传 Excel 文件！');
    return false; // 阻止自动上传
  }

  // 调用自定义上传方法
  uploadFile(file);
  return false; // 阻止自动上传
};

// 自定义上传方法
const uploadFile = async (file) => {
  isUploading.value = true;

  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await axios.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    SuccessPop('文件上传成功！');
    fetchRecords(); // 上传成功后刷新表格数据
  } catch (error) {
    ErrorPop(error.response.data.error);
    console.error(error);
  } finally {
    isUploading.value = false;
  }
};
</script>

<style scoped>
.table-wrapper {
  margin-top: 20px;
  padding: 20px;
  background-color: #ffffff;
  border: 1px solid #ebeef5;
  border-radius: 12px; /* 圆角 */
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1); /* 阴影效果 */
}

.operations {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.left-buttons {
  display: flex;
  align-items: center;
}

.right-search {
  display: flex;
  align-items: center;
}

.table-container {
  /* 表格容器内部样式 */
  max-height: 100%; /* 与表格高度一致 */
  overflow: auto; /* 启用内部滚动 */
  border: 1px solid #ebeef5;
  border-radius: 8px;
}

.table {
  width: 100%;
  font-size: 16px;
  /* 不需要额外的高度设置，因为表格的高度已经通过 `height` 属性设置 */
}

.table-cell {
  display: flex;
  justify-content: center;
  align-items: center;
  width: auto;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .operations {
    flex-direction: column;
    align-items: flex-start;
  }

  .right-search {
    margin-top: 10px;
    width: 100%;
  }

  .right-search .el-input {
    width: 100%;
  }

  .left-buttons {
    flex-wrap: wrap;
  }

  .left-buttons .el-button {
    margin-bottom: 10px;
  }
}
</style>
