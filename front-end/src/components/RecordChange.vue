<template>
  <!-- 创建一个表单，绑定到 `recordForm`，label-width 为自动，最大宽度 400px -->
  <el-form :model="recordForm" label-width="auto" style="max-width: 500px" label-position="top" status-icon
           :rules="rules" ref="recordFormRef">

    <!-- 时间选择 -->
    <el-form-item label="时间" required prop="time">
      <el-col :span="11">
        <!-- 日期选择器 -->
        <el-date-picker
            v-model="recordForm.date"
            type="date"
            placeholder="选择日期"
            style="width: 100%"
        />
      </el-col>
      <el-col :span="2" class="text-center">
        <span class="text-gray-500"></span>
      </el-col>
      <el-col :span="11">
        <!-- 时间选择器 -->
        <el-time-picker
            v-model="recordForm.time"
            placeholder="选择时间"
            style="width: 100%"
            format="HH:mm"
        />
      </el-col>
    </el-form-item>

    <!-- 金额输入框 -->
    <el-form-item label="金额" required prop="amount">
      <el-input v-model="recordForm.amount" placeholder="输入金额" type="number">
        <!-- 输入框前缀区域，添加图标 -->
        <template #prepend>
          <el-button :icon="Money" size="large">
          </el-button>
        </template>
        <!-- 输入框后缀区域，添加单位 -->
        <template #append>元</template>
      </el-input>
    </el-form-item>

    <!-- 类型单选框 -->
    <el-form-item label="类型" required prop="type">
      <el-radio-group v-model="recordForm.type" size="large">
        <!-- 资源选项：收入 -->
        <el-radio value="income" style="margin-right: 150px; margin-left: 100px">收入</el-radio>
        <!-- 资源选项：支出 -->
        <el-radio value="expense">支出</el-radio>
      </el-radio-group>
    </el-form-item>


    <!-- 类别选择框 -->
    <el-form-item label="类别" required prop="category">
      <!-- 类别选择框，点击时会触发 `updateCategoryList` 方法更新类别列表 -->
      <el-select v-model="recordForm.category" placeholder="请选择类别" @click="updateCategoryList">
        <el-option v-for="category in categoryList" :label="category" :value="category"/>
      </el-select>
    </el-form-item>

    <!-- 描述文本框 -->
    <el-form-item label="备注">
      <!-- 文本框，`v-model` 双向绑定 `recordForm.note` -->
      <el-input v-model="recordForm.note" type="textarea" maxlength="50"/>
    </el-form-item>

    <!-- 提交按钮与取消按钮 -->

    <div style="display: flex; justify-content: center; gap: 10px;">
      <el-button type="primary" @click="onSubmit">{{ word }}</el-button>
      <el-button @click="handleCancel">取消</el-button>
    </div>

  </el-form>
</template>

<script setup>
// 导入所需的 Vue 函数和 Element Plus 的组件
import {reactive, ref} from 'vue';
import {ElMessage} from "element-plus";
import {Money} from '@element-plus/icons-vue';
import axios from "axios";



// 表单引用，用于验证
const recordFormRef = ref(null);
// 提交按钮文字
let word = ref("添加");
//判断是添加还是更改
let operationTip = false

const emit = defineEmits(['cancel', 'success']);


const handleCancel = () => {
  emit('cancel');
}

// 创建表单的响应式数据对象 `recordForm`，用于绑定表单项的值
let recordForm = reactive({
  date: '',  // 日期
  time: '',  // 时间
  amount: null,  // 金额
  type: '',  // 类型：收入或支出
  category: '',  // 类别
  note: '',  // 备注
  timeStamp: 0,  // 时间戳
  id: null
});


//初始化表单,tip(true=添加,false=更改)
const initForm = (tip, form) => {
  if (tip) {
    Object.assign(recordForm, {
      date: formatDate(new Date()),            // 日期
      time: formatDate(new Date()),  // 时间
      amount: null,                  // 金额
      type: '',                      // 类型：收入或支出
      category: '',                  // 类别
      note: '',                      // 备注
      timeStamp: 0,                  // 时间戳
      id: null
    });
    word.value = "添加";
  } else {
    Object.assign(recordForm, form);
    word.value = "确定";
  }
  operationTip = tip;
  clearValidationErrors();
}

// 清除表单验证错误的函数
const clearValidationErrors = () => {
  if (recordFormRef.value) {
    recordFormRef.value.clearValidate();
  }
}

//暴露函数
defineExpose({initForm})

// 表单验证规则
const rules = {
  date: [
    {required: true, message: '请选择日期', trigger: 'blur'},
  ],
  time: [
    {required: true, message: '请选择时间', trigger: 'blur'},
  ],
  amount: [
    {required: true, message: '请输入金额', trigger: 'blur'},
  ],
  type: [
    {required: true, message: '请选择类型', trigger: 'blur'},
  ],
  category: [
    {required: true, message: '请选择类别', trigger: 'blur'},
  ],
};

// 提交表单的方法
const onSubmit = () => {
  // 校验表单是否有效
  recordFormRef.value.validate((valid) => {
    if (valid) {
      dateToTimeStamp(recordForm.date, recordForm.time); //写入时间戳
      console.log("发送", recordForm);
      if (operationTip) {
        addRecord();
      } else {
        editRecord()
      }

    } else {
      // 如果验证失败，弹出错误提示
      ErrorPop('请填写完整信息');
    }
  });
};

// 分类逻辑
const categories = {
  'income': [
    '工资收入', '奖金津贴', '投资收入', '利息收入', '租金收入', '其他收入',
  ],
  'expense': [
    '房租', '水电煤气', '交通费', '餐饮', '保险费用', '娱乐休闲', '医疗健康', '教育支出', '购物消费', '贷款还款', '税费', '其他支出',
  ]
};

// 用于保存类别列表
let categoryList = ref([]);

// 根据选择的类型更新类别列表
const updateCategoryList = () => {
  if (recordForm.type) {
    const type = recordForm.type;
    categoryList.value = categories[type];
  } else {
    categoryList.value = [];
    WarningPop("请先选择类型(收入/支出)");
  }
};

// 初始化时间
const man = () => {
  const currentDate = new Date();
  const initTime = formatDate(currentDate);
  recordForm.date = initTime;
  recordForm.time = initTime;
};

//添加记录
const addRecord = async () => {
  try {
    const response = await axios.post('/records', recordForm);
    const msg = response.data.message;
    SuccessPop(msg);
    emit('success');
  } catch (error) {
    const msg = error.response.data.error
    ErrorPop(msg);
  }
};

//编辑记录
const editRecord = async () => {
  try {
    const response = await axios.put(`/records/${recordForm.id}`, recordForm);
    const msg = response.data.message;
    SuccessPop(msg);
    emit('success');
  } catch (error) {
    const msg = error.response.data.error
    ErrorPop(msg);
  }
};


// 将表单的日期和时间转换为时间戳
const dateToTimeStamp = (date, time) => {
  const formDate = formatDate(date);
  const formTime = formatDate(time);
  const dateObject = combineDateTime(formDate.substring(0, 10), formTime.substring(10));
  // return dateObject.getTime();
  recordForm.timeStamp = dateObject.getTime();
};

// 将字符串日期统一格式化为 "2024-12-31 14:30" 格式
const formatDate = (date) => {
  const d = new Date(date);
  const year = d.getFullYear();
  const month = (d.getMonth() + 1).toString().padStart(2, '0');
  const day = d.getDate().toString().padStart(2, '0');
  const hours = d.getHours().toString().padStart(2, '0');
  const minutes = d.getMinutes().toString().padStart(2, '0');
  const seconds = d.getSeconds().toString().padStart(2, '0');
  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
};

// 拼接格式化后的日期和时间成有效的 Date 对象
const combineDateTime = (date, time) => {
  const dateTimeString = `${date} ${time}`;
  return new Date(dateTimeString);
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
</script>
