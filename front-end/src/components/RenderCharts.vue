<template>
  <div class="summary-chart-container">
    <el-card class="controls-card">
      <el-row align="middle">
        <el-col :span="4">
          <label for="period-select" class="control-label">选择时间粒度:</label>
        </el-col>
        <el-col :span="8">
          <el-select v-model="selectedPeriod" placeholder="请选择" @change="fetchSummaryData" style="width: 100%;">
            <el-option label="按年" value="year"></el-option>
            <el-option label="按月" value="month"></el-option>
            <el-option label="按日" value="day"></el-option>
            <el-option label="整体" value="overall"></el-option>
          </el-select>
        </el-col>
      </el-row>
    </el-card>

    <el-row gutter={20}>
      <el-col :span="24">
        <el-card>
          <div ref="lineChart" class="chart"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row gutter={20} class="pie-charts">
      <el-col :span="24" :md="12">
        <el-card>
          <div ref="incomePieChart" class="pie-chart"></div>
        </el-card>
      </el-col>
      <el-col :span="24" :md="12">
        <el-card>
          <div ref="expensePieChart" class="pie-chart"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Loading Indicator -->
    <el-loading :fullscreen="fullscreenLoading" text="加载中..."></el-loading>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue';
import axios from 'axios';
import * as echarts from 'echarts';
import { ElMessage } from 'element-plus';

// 定义响应式数据
const selectedPeriod = ref('year'); // 默认选择按年汇总
const summaryData = ref([]);
const pieData = ref({
  period: '',
  year: null,
  month: null,
  day: null,
  income_categories: [],
  expense_categories: []
});
const lineChart = ref(null);
const incomePieChart = ref(null);
const expensePieChart = ref(null);
let lineChartInstance = null;
let incomePieChartInstance = null;
let expensePieChartInstance = null;

// Loading 状态
const fullscreenLoading = ref(false);

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

// 获取汇总数据
const fetchSummaryData = async () => {
  fullscreenLoading.value = true;
  try {
    const response = await axios.get('/summary', {
      params: {period: selectedPeriod.value},
    });

    if (response.status === 200) {
      summaryData.value = response.data.summary;
      renderLineChart();
      // 清空之前的饼图数据
      pieData.value = {
        period: '',
        year: null,
        month: null,
        day: null,
        income_categories: [],
        expense_categories: []
      };
      renderPieCharts(); // 清空饼图
    } else {
      WarningPop('获取汇总数据失败。');
    }
  } catch (error) {
    console.error('Error fetching summary data:', error);
    WarningPop('获取汇总数据时出错。');
  } finally {
    fullscreenLoading.value = false;
  }
};

// 获取饼图数据
const fetchPieData = async (timeParams) => {
  fullscreenLoading.value = true;
  try {
    const response = await axios.get('/summary_pie', {
      params: timeParams,
    });

    if (response.status === 200) {
      pieData.value = response.data;
      renderPieCharts();
    } else {
      WarningPop('获取分类汇总数据失败。');
    }
  } catch (error) {
    console.error('Error fetching pie data:', error);
    WarningPop('获取分类汇总数据时出错。');
  } finally {
    fullscreenLoading.value = false;
  }
};

// 获取时间描述
const getTimeDescription = () => {
  const {period, year, month, day} = pieData.value;
  if (period === 'year') {
    return `${year}年的`;
  } else if (period === 'month的') {
    return `${year}年${month}月的`;
  } else if (period === 'day') {
    return `${year}年${month}月${day}日的`;
  } else if (period === 'overall') {
    return '整体的';
  }
  return '空白的';
};

// 渲染折线图
const renderLineChart = () => {
  if (!lineChartInstance) {
    lineChartInstance = echarts.init(lineChart.value);
  }

  const {xData, incomeData, expenseData, balanceData} = processLineData();

  const option = {
    title: {
      text: '收入、支出与结余折线图',
      left: 'center',
      textStyle: {
        fontSize: 18,
        fontWeight: 'bold'
      }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    legend: {
      data: ['总收入', '总支出', '结余'],
      top: 30
    },
    grid: {
      left: '10%',
      right: '10%',
      bottom: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: xData,
      axisLabel: {
        formatter: (value) => value
      }
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: '{value} 元'
      }
    },
    series: [
      {
        name: '总收入',
        type: 'line',
        data: incomeData,
        smooth: true,
        lineStyle: {
          color: '#3FB1E3'
        },
        areaStyle: {
          color: 'rgba(63, 177, 227, 0.2)'
        }
      },
      {
        name: '总支出',
        type: 'line',
        data: expenseData,
        smooth: true,
        lineStyle: {
          color: '#FF6E7F'
        },
        areaStyle: {
          color: 'rgba(255, 110, 127, 0.2)'
        }
      },
      {
        name: '结余',
        type: 'line',
        data: balanceData,
        smooth: true,
        lineStyle: {
          color: '#7ECF51'
        },
        areaStyle: {
          color: 'rgba(126, 207, 81, 0.2)'
        }
      }
    ]
  };

  lineChartInstance.setOption(option);

  // 移除之前的点击事件监听器，防止重复绑定
  lineChartInstance.off('click');

  // 添加点击事件
  lineChartInstance.on('click', function (params) {
    // 根据 selectedPeriod 获取对应的时间参数
    let timeParams = {period: selectedPeriod.value};

    // 使用正则表达式精确提取时间参数
    if (selectedPeriod.value === 'year') {
      const regex = /^(\d+)年$/;
      const match = params.name.match(regex);
      if (match) {
        timeParams.year = parseInt(match[1]);
      } else {
        WarningPop('时间格式错误。');
        return;
      }
    } else if (selectedPeriod.value === 'month') {
      const regex = /^(\d+)年(\d+)月$/;
      const match = params.name.match(regex);
      if (match) {
        timeParams.year = parseInt(match[1]);
        timeParams.month = parseInt(match[2]);
      } else {
        WarningPop('时间格式错误。');
        return;
      }
    } else if (selectedPeriod.value === 'day') {
      const regex = /^(\d+)年(\d+)月(\d+)日$/;
      const match = params.name.match(regex);
      if (match) {
        timeParams.year = parseInt(match[1]);
        timeParams.month = parseInt(match[2]);
        timeParams.day = parseInt(match[3]);
      } else {
        WarningPop('时间格式错误。');
        return;
      }
    }
    // 'overall' 无需额外参数

    console.log('请求饼图数据的参数:', timeParams); // 调试信息

    // 触发获取饼图数据
    fetchPieData(timeParams);
  });

  window.addEventListener('resize', lineChartInstance.resize);
};

// 渲染饼图
const renderPieCharts = () => {
  if (!incomePieChartInstance) {
    incomePieChartInstance = echarts.init(incomePieChart.value);
  }

  if (!expensePieChartInstance) {
    expensePieChartInstance = echarts.init(expensePieChart.value);
  }

  const timeDesc = getTimeDescription();

  const incomeOption = {
    title: {
      text: `${timeDesc}收入分类分布`,
      left: 'center',
      textStyle: {
        fontSize: 16,
        fontWeight: 'bold'
      }
    },
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} 元 ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [
      {
        name: '收入分类',
        type: 'pie',
        radius: '50%',
        data: pieData.value.income_categories.map(item => ({
          value: item.amount,
          name: item.category
        })),
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
    title: {
      text: `${timeDesc}支出分类分布`,
      left: 'center',
      textStyle: {
        fontSize: 16,
        fontWeight: 'bold'
      }
    },
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} 元 ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [
      {
        name: '支出分类',
        type: 'pie',
        radius: '50%',
        data: pieData.value.expense_categories.map(item => ({
          value: item.amount,
          name: item.category
        })),
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

  incomePieChartInstance.setOption(incomeOption);
  expensePieChartInstance.setOption(expenseOption);

  window.addEventListener('resize', incomePieChartInstance.resize);
  window.addEventListener('resize', expensePieChartInstance.resize);
};

// 处理折线图数据
const processLineData = () => {
  const xData = [];
  const incomeData = [];
  const expenseData = [];
  const balanceData = [];

  summaryData.value.forEach(item => {
    if (selectedPeriod.value === 'year') {
      xData.push(`${item.year}年`);
    } else if (selectedPeriod.value === 'month') {
      xData.push(`${item.year}年${item.month}月`);
    } else if (selectedPeriod.value === 'day') {
      xData.push(`${item.year}年${item.month}月${item.day}日`);
    } else if (selectedPeriod.value === 'overall') {
      xData.push('整体');
    }

    incomeData.push(item.total_income);
    expenseData.push(item.total_expense);
    balanceData.push(item.balance);
  });

  return {xData, incomeData, expenseData, balanceData};
};

// 生命周期钩子
onMounted(() => {
  fetchSummaryData();
});

onBeforeUnmount(() => {
  if (lineChartInstance) {
    lineChartInstance.dispose();
  }
  if (incomePieChartInstance) {
    incomePieChartInstance.dispose();
  }
  if (expensePieChartInstance) {
    expensePieChartInstance.dispose();
  }
  window.removeEventListener('resize', lineChartInstance?.resize);
  window.removeEventListener('resize', incomePieChartInstance?.resize);
  window.removeEventListener('resize', expensePieChartInstance?.resize);
});
</script>

<style scoped>
.summary-chart-container {
  width: 100%;
  max-width: 1200px;
  margin: 20px auto;
}

.controls-card {
  margin-bottom: 20px;
  padding: 20px;
}

.control-label {
  font-weight: bold;
  display: block;
  margin-bottom: 5px;
}

.chart {
  width: 100%;
  height: 500px;
}

.pie-charts {
  margin-top: 20px;
}

.pie-chart {
  width: 100%;
  height: 400px;
}
</style>
