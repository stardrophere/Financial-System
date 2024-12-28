<template>
  <div class="financial-report-container">
    <el-card class="controls-card">
      <el-form :inline="true" :model="form" class="report-form">
        <el-form-item label="选择时间范围">
          <el-date-picker
              v-model="form.dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              style="width: 300px;"
          >
          </el-date-picker>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="generateReport" :loading="loading">
            生成报告
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card v-if="reportData" class="report-preview" ref="report">
      <div class="report-preview-scrollable">
        <h2 class="report-title">财务信息报告</h2>
        <p class="report-period">时间范围：{{ reportPeriod }}</p>

        <el-row :gutter="20">
          <el-col :span="8">
            <el-card>
              <div class="summary-item">
                <span class="summary-label">总收入：</span>
                <span class="summary-value">{{ reportData.total_income }} 元</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card>
              <div class="summary-item">
                <span class="summary-label">总支出：</span>
                <span class="summary-value">{{ reportData.total_expense }} 元</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card>
              <div class="summary-item">
                <span class="summary-label">结余：</span>
                <span class="summary-value">{{ reportData.balance }} 元</span>
              </div>
            </el-card>
          </el-col>
        </el-row>

        <el-row :gutter="20" class="charts-row">
          <el-col :span="12">
            <el-card>
              <h3 class="chart-title">收入日期分布</h3>
              <div ref="incomePieChart" class="chart"></div>
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card>
              <h3 class="chart-title">支出日期分布</h3>
              <div ref="expensePieChart" class="chart"></div>
            </el-card>
          </el-col>
        </el-row>

        <el-row class="daily-list-row" style="margin-top: 20px;">
          <el-col :span="24">
            <el-card>
              <h3 class="list-title">每日收入与支出详情</h3>
              <el-table :data="dailyData" style="width: 100%">
                <el-table-column prop="date" label="日期" align="center"></el-table-column>
                <el-table-column prop="income" label="收入" align="center"></el-table-column>
                <el-table-column prop="expense" label="支出" align="center"></el-table-column>
                <el-table-column prop="balance" label="结余" align="center"></el-table-column>
              </el-table>

            </el-card>
          </el-col>
        </el-row>
      </div>


      <el-row class="download-button-row">
        <el-col :span="24" style="text-align: center;">
          <el-button type="success" @click="downloadImage">下载图片</el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- Loading Indicator -->
    <el-loading :fullscreen="fullscreenLoading" text="加载中..."></el-loading>

    <!-- Error Message -->
    <el-alert
        v-if="error"
        :title="error"
        type="error"
        show-icon
        closable
        @close="error = ''"
        class="error-alert"
    ></el-alert>
  </div>
</template>

<script setup>
import {ref, onMounted, watch, nextTick} from 'vue';
import axios from 'axios';
import * as echarts from 'echarts';
import {ElMessage} from 'element-plus';
import html2canvas from 'html2canvas';

const form = ref({
  dateRange: []
});
const loading = ref(false);
const fullscreenLoading = ref(false);
const reportData = ref(null);
const error = ref('');
const reportPeriod = ref('');

const incomePieChart = ref(null);
const expensePieChart = ref(null);

let incomePieChartInstance = null;
let expensePieChartInstance = null;

const getTimeDescription = (start, end) => {
  if (!start || !end) return '';
  const options = {year: 'numeric', month: 'numeric', day: 'numeric'};
  const startDate = new Date(start).toLocaleDateString('zh-CN', options);
  const endDate = new Date(end).toLocaleDateString('zh-CN', options);
  return `${startDate} 至 ${endDate}`;
};


const dailyData = ref([]); // 每日数据列表

const generateReport = async () => {
  if (!form.value.dateRange || form.value.dateRange.length !== 2) {
    ElMessage({
      message: '请选择有效的时间范围。',
      type: 'warning',
      duration: 3000
    });
    return;
  }

  const [startDate, endDate] = form.value.dateRange.map(date =>
      new Date(date).toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
      }).replace(/\//g, '-')
  );

  const timeParams = {
    period: 'custom',
    start_date: startDate, // 确保是 "YYYY-MM-DD" 格式
    end_date: endDate
  };


  fullscreenLoading.value = true;
  loading.value = true;
  error.value = '';
  reportData.value = null;
  reportPeriod.value = getTimeDescription(startDate, endDate);

  try {
    const summaryResponse = await axios.get('/summary', {params: timeParams});
    console.log(timeParams);
    console.log('后端返回的汇总数据:', summaryResponse.data);

    if (summaryResponse.status === 200) {
      const summary = summaryResponse.data.summary;

      // 总计收入、支出、结余
      const totalIncome = summary.reduce((sum, item) => sum + (item.total_income || 0), 0);
      const totalExpense = summary.reduce((sum, item) => sum + (item.total_expense || 0), 0);
      const balance = totalIncome - totalExpense;

      // 更新饼图数据
      const incomeCategories = summary
          .filter(item => item.total_income > 0)
          .map(item => ({
            category: `${item.year}-${item.month}-${item.day}`,
            amount: item.total_income
          }));

      const expenseCategories = summary
          .filter(item => item.total_expense > 0)
          .map(item => ({
            category: `${item.year}-${item.month}-${item.day}`,
            amount: item.total_expense
          }));

      // 更新每日数据列表
      dailyData.value = summary.map(item => ({
        date: `${item.year}-${item.month}-${item.day}`,
        income: item.total_income || 0,
        expense: item.total_expense || 0,
        balance: item.balance || 0
      }));

      // 更新报告数据
      reportData.value = {
        total_income: totalIncome,
        total_expense: totalExpense,
        balance: balance,
        income_categories: incomeCategories,
        expense_categories: expenseCategories
      };

      // 渲染图表
      await nextTick();
      renderPieCharts();
    } else {
      error.value = '获取汇总数据失败。';
    }
  } catch (err) {
    console.error('Error generating report:', err);
    error.value = '生成报告时出错。';
  } finally {
    fullscreenLoading.value = false;
    loading.value = false;
  }
};


const renderPieCharts = () => {
  // 检查 DOM 元素是否已挂载
  if (!incomePieChart.value || !expensePieChart.value) {
    console.error('图表容器未加载完成');
    return;
  }

  // 销毁旧实例（如果存在）
  if (incomePieChartInstance) {
    incomePieChartInstance.dispose();
    incomePieChartInstance = null;
  }
  if (expensePieChartInstance) {
    expensePieChartInstance.dispose();
    expensePieChartInstance = null;
  }

  // 初始化新的实例
  incomePieChartInstance = echarts.init(incomePieChart.value);
  expensePieChartInstance = echarts.init(expensePieChart.value);

  const incomeData = reportData.value?.income_categories || [];
  const expenseData = reportData.value?.expense_categories || [];

  const incomeOption = {
    tooltip: {trigger: 'item', formatter: '{b}: {c} 元 ({d}%)'},
    legend: {
      orient: 'vertical',
      left: 'left',
      data: incomeData.map(item => item.category)
    },
    series: [
      {
        name: '收入分类',
        type: 'pie',
        radius: '50%',
        data: incomeData.map(item => ({value: item.amount, name: item.category})),
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  };

  const expenseOption = {
    tooltip: {trigger: 'item', formatter: '{b}: {c} 元 ({d}%)'},
    legend: {
      orient: 'vertical',
      left: 'left',
      data: expenseData.map(item => item.category)
    },
    series: [
      {
        name: '支出分类',
        type: 'pie',
        radius: '50%',
        data: expenseData.map(item => ({value: item.amount, name: item.category})),
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  };

  // 更新图表
  incomePieChartInstance.setOption(incomeOption);
  expensePieChartInstance.setOption(expenseOption);
};


const downloadImage = async () => {
  const element = document.querySelector('.report-preview'); // 选择要截图的元素

  try {
    const canvas = await html2canvas(element, {
      scale: 3,         // 提高分辨率
      useCORS: true,    // 允许跨域加载图片
      ignoreElements: (el) => {
        // 忽略下载按钮容器
        return el.classList && el.classList.contains('download-button-row');
      }
    });

    const link = document.createElement('a');
    link.download = `财务信息报告_${reportPeriod.value}.png`;
    link.href = canvas.toDataURL('image/png');
    link.click();
  } catch (error) {
    console.error('Error generating image:', error);
    ElMessage.error('生成图片时出错，请重试');
  }
};

</script>


<style scoped>
.financial-report-container {
  width: 100%;
  max-width: 1200px;
  margin: 20px auto;
}

.controls-card {
  margin-bottom: 20px;
  padding: 20px;
}

.report-form {
  width: 100%;
}

.report-preview {
  padding: 20px;
  background-color: #fff;
}

.report-title {
  text-align: center;
  margin-bottom: 10px;
}

.report-period {
  text-align: center;
  margin-bottom: 20px;
  font-weight: bold;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  font-size: 18px;
}

.summary-label {
  font-weight: bold;
}

.summary-value {
  color: #409EFF;
}

.charts-row {
  margin-top: 20px;
}

.chart-title {
  text-align: center;
  margin-bottom: 10px;
}

.chart {
  width: 100%;
  height: 400px;
}

.download-button-row {
  margin-top: 20px;
}

.error-alert {
  margin-top: 20px;
}

.daily-list-row {
  margin-top: 20px;
}

.list-title {
  text-align: center;
  margin-bottom: 20px;
}

.el-table {
  font-size: 14px;
  text-align: center;
}

</style>
