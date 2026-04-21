<template>
  <div class="dashboard">
    <h1 class="dashboard-title">审核工作台</h1>
    
    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon pending">📋</div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.pending }}</div>
          <div class="stat-label">待审核</div>
        </div>
        <div class="stat-trend">
          <span class="trend-icon">↗</span>
          <span class="trend-text">+12%</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon in-review">🔍</div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.in_review }}</div>
          <div class="stat-label">审核中</div>
        </div>
        <div class="stat-trend">
          <span class="trend-icon">→</span>
          <span class="trend-text">0%</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon approved">✅</div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.approved }}</div>
          <div class="stat-label">已通过</div>
        </div>
        <div class="stat-trend">
          <span class="trend-icon">↗</span>
          <span class="trend-text">+25%</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon rejected">❌</div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.rejected }}</div>
          <div class="stat-label">已驳回</div>
        </div>
        <div class="stat-trend">
          <span class="trend-icon">↘</span>
          <span class="trend-text">-8%</span>
        </div>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="charts-grid">
      <div class="card chart-card">
        <h3 class="card-title">审核状态分布</h3>
        <div class="chart-container">
          <canvas ref="statusChart"></canvas>
        </div>
      </div>
      <div class="card chart-card">
        <h3 class="card-title">审核趋势</h3>
        <div class="chart-container">
          <canvas ref="trendChart"></canvas>
        </div>
      </div>
    </div>

    <!-- 任务区域 -->
    <div class="dashboard-row">
      <div class="card my-tasks">
        <h3 class="card-title">我的任务</h3>
        <div class="my-stats">
          <div class="my-stat">
            <span class="my-stat-value">{{ stats.my_pending }}</span>
            <span class="my-stat-label">待处理</span>
          </div>
          <div class="my-stat">
            <span class="my-stat-value">{{ stats.today_reviewed }}</span>
            <span class="my-stat-label">今日已审核</span>
          </div>
          <div class="my-stat">
            <span class="my-stat-value">{{ stats.my_completed }}</span>
            <span class="my-stat-label">累计审核</span>
          </div>
        </div>
        <router-link to="/review/pending" class="btn-primary" style="display: inline-block; margin-top: 16px;">
          查看待审核任务
        </router-link>
      </div>

      <div class="card recent-tasks">
        <h3 class="card-title">最近任务</h3>
        <div v-if="recentTasks.length === 0" class="empty">暂无任务</div>
        <div v-else class="tasks-table">
          <table>
            <thead>
              <tr>
                <th>教材名称</th>
                <th>状态</th>
                <th>提交时间</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="task in recentTasks" :key="task.id" class="task-row">
                <td class="task-title">{{ task.book_title }}</td>
                <td>
                  <span :class="['status-badge', `status-${task.status}`]">
                    {{ task.status_display }}
                  </span>
                </td>
                <td>{{ formatDate(task.created_at) }}</td>
                <td>
                  <router-link :to="`/review/review/${task.id}`" class="btn-default" style="padding: 4px 12px;">
                    查看
                  </router-link>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { taskApi } from '../api/review'
import Chart from 'chart.js/auto'

const stats = ref({
  total: 0,
  pending: 0,
  in_review: 0,
  approved: 0,
  rejected: 0,
  today_reviewed: 0,
  my_pending: 0,
  my_completed: 0
})

const recentTasks = ref([])
const statusChart = ref(null)
const trendChart = ref(null)
let statusChartInstance = null
let trendChartInstance = null

const loadStats = async () => {
  try {
    const data = await taskApi.getStats()
    stats.value = data
    updateCharts()
  } catch (err) {
    console.error('加载统计失败', err)
  }
}

const loadRecentTasks = async () => {
  try {
    const data = await taskApi.getList({ page_size: 5 })
    recentTasks.value = data.results || data
  } catch (err) {
    console.error('加载最近任务失败', err)
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const updateCharts = () => {
  // 状态分布图表
  if (statusChart.value) {
    if (statusChartInstance) {
      statusChartInstance.destroy()
    }
    
    statusChartInstance = new Chart(statusChart.value, {
      type: 'doughnut',
      data: {
        labels: ['待审核', '审核中', '已通过', '已驳回'],
        datasets: [{
          data: [stats.value.pending, stats.value.in_review, stats.value.approved, stats.value.rejected],
          backgroundColor: [
            '#ff9800',
            '#2196f3',
            '#4caf50',
            '#f44336'
          ],
          borderWidth: 0
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom'
          }
        }
      }
    })
  }
  
  // 审核趋势图表
  if (trendChart.value) {
    if (trendChartInstance) {
      trendChartInstance.destroy()
    }
    
    // 模拟最近7天的数据
    const labels = ['7天前', '6天前', '5天前', '4天前', '3天前', '2天前', '今天']
    const data = [12, 19, 15, 25, 22, 30, stats.value.today_reviewed]
    
    trendChartInstance = new Chart(trendChart.value, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [{
          label: '审核数量',
          data: data,
          borderColor: '#2196f3',
          backgroundColor: 'rgba(33, 150, 243, 0.1)',
          tension: 0.4,
          fill: true
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true,
            grid: {
              drawBorder: false
            }
          },
          x: {
            grid: {
              display: false
            }
          }
        }
      }
    })
  }
}

onMounted(() => {
  loadStats()
  loadRecentTasks()
  // 延迟初始化图表，确保DOM已渲染
  setTimeout(() => {
    updateCharts()
  }, 100)
})

onUnmounted(() => {
  if (statusChartInstance) {
    statusChartInstance.destroy()
  }
  if (trendChartInstance) {
    trendChartInstance.destroy()
  }
})
</script>

<style scoped>
.dashboard {
  padding: 24px;
}

.dashboard-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-color);
  margin-bottom: 24px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 32px;
}

.stat-card {
  background: var(--white);
  border-radius: 12px;
  padding: 24px;
  display: flex;
  align-items: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.stat-icon {
  width: 70px;
  height: 70px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  margin-right: 20px;
  flex-shrink: 0;
}

.stat-icon.pending { 
  background: linear-gradient(135deg, #fff7e6, #ffcc80); 
}
.stat-icon.in-review { 
  background: linear-gradient(135deg, #e6f7ff, #64b5f6); 
}
.stat-icon.approved { 
  background: linear-gradient(135deg, #f6ffed, #81c784); 
}
.stat-icon.rejected { 
  background: linear-gradient(135deg, #fff2f0, #e57373); 
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: var(--text-color);
  line-height: 1;
}

.stat-label {
  color: var(--text-secondary);
  margin-top: 8px;
  font-size: 14px;
}

.stat-trend {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  margin-left: 16px;
}

.trend-icon {
  font-size: 16px;
  margin-bottom: 4px;
}

.trend-text {
  font-size: 12px;
  font-weight: 600;
  color: #4caf50;
}

.charts-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-bottom: 32px;
}

.chart-card {
  background: var(--white);
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.chart-container {
  height: 300px;
  margin-top: 16px;
}

.dashboard-row {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 24px;
}

.card {
  background: var(--white);
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-color);
  color: var(--text-color);
}

.my-stats {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 16px 0;
}

.my-stat {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
}

.my-stat-value {
  font-size: 24px;
  font-weight: bold;
  color: var(--primary-color);
}

.my-stat-label {
  color: var(--text-secondary);
  font-size: 14px;
}

.tasks-table {
  overflow-x: auto;
}

.tasks-table table {
  width: 100%;
  border-collapse: collapse;
}

.tasks-table th,
.tasks-table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
}

.tasks-table th {
  font-weight: 600;
  color: var(--text-secondary);
  font-size: 14px;
}

.task-row:hover {
  background-color: #f8f9fa;
}

.task-title {
  font-weight: 500;
  color: var(--text-color);
}

.status-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.status-pending {
  background: #fff7e6;
  color: #ff9800;
}

.status-in_review {
  background: #e6f7ff;
  color: #2196f3;
}

.status-approved {
  background: #f6ffed;
  color: #4caf50;
}

.status-rejected {
  background: #fff2f0;
  color: #f44336;
}

.empty {
  text-align: center;
  padding: 40px 0;
  color: var(--text-secondary);
  font-style: italic;
}

@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .charts-grid {
    grid-template-columns: 1fr;
  }
  
  .dashboard-row {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .dashboard {
    padding: 16px;
  }
}
</style>
