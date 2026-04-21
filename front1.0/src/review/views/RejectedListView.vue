<template>
  <div class="rejected-list">
    <h1 class="page-title">已驳回任务</h1>
    
    <!-- 统计卡片 -->
    <div class="stats-cards">
      <div class="stat-card">
        <div class="stat-icon rejected">❌</div>
        <div class="stat-info">
          <div class="stat-value">{{ totalCount }}</div>
          <div class="stat-label">已驳回任务</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon total">📊</div>
        <div class="stat-info">
          <div class="stat-value">{{ totalPages }}</div>
          <div class="stat-label">总页数</div>
        </div>
      </div>
    </div>

    <!-- 筛选栏 -->
    <div class="filter-bar card">
      <div class="filter-row">
        <div class="filter-item">
          <label>类型：</label>
          <select v-model="filters.task_type" @change="loadTasks" class="filter-select">
            <option value="">全部</option>
            <option value="new_submission">新提交</option>
            <option value="edit_review">修改审核</option>
          </select>
        </div>
        <div class="filter-item search-item">
          <label>搜索：</label>
          <div class="search-box">
            <input 
              v-model="filters.search" 
              placeholder="教材名称/作者"
              @keyup.enter="loadTasks"
              class="search-input"
            />
            <button class="btn-primary search-btn" @click="loadTasks">搜索</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 任务列表 -->
    <div class="card task-list-card">
      <div v-if="loading" class="loading">
        <div class="loading-spinner"></div>
        <span>加载中...</span>
      </div>
      <div v-else-if="tasks.length === 0" class="empty">
        <div class="empty-icon">❌</div>
        <h3>暂无已驳回任务</h3>
        <p>当前没有已驳回的教材</p>
      </div>
      <div v-else class="tasks-table-container">
        <table class="tasks-table">
          <thead>
            <tr>
              <th>教材名称</th>
              <th>作者</th>
              <th>类型</th>
              <th>审核人</th>
              <th>驳回时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="task in tasks" :key="task.id" class="task-row">
              <td class="task-title">
                <router-link :to="`/review/review/${task.id}`">{{ task.book_title }}</router-link>
              </td>
              <td>{{ task.book_author }}</td>
              <td>{{ task.task_type_display }}</td>
              <td>{{ task.assigned_reviewer_name || '-' }}</td>
              <td>{{ formatDate(task.updated_at) }}</td>
              <td>
                <router-link :to="`/review/review/${task.id}`" class="btn-default task-btn">
                  查看
                </router-link>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 分页 -->
      <div v-if="totalPages > 1" class="pagination">
        <button 
          class="btn-default page-btn" 
          :disabled="currentPage === 1"
          @click="changePage(currentPage - 1)"
        >
          <span class="page-icon">←</span> 上一页
        </button>
        <div class="page-info">
          <span>第 {{ currentPage }} / {{ totalPages }} 页</span>
          <span class="total-count">共 {{ totalCount }} 条</span>
        </div>
        <button 
          class="btn-default page-btn" 
          :disabled="currentPage === totalPages"
          @click="changePage(currentPage + 1)"
        >
          下一页 <span class="page-icon">→</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { taskApi } from '../api/review'

const tasks = ref([])
const loading = ref(false)
const currentPage = ref(1)
const totalPages = ref(1)
const totalCount = ref(0)

const filters = ref({
  task_type: '',
  search: ''
})

const loadTasks = async () => {
  loading.value = true
  try {
    const params = {
      status: 'rejected',
      page: currentPage.value,
      ...filters.value
    }
    const data = await taskApi.getList(params)
    tasks.value = data.results || data
    totalCount.value = data.count || tasks.value.length
    totalPages.value = Math.ceil(totalCount.value / 20)
  } catch (err) {
    console.error('加载失败', err)
  } finally {
    loading.value = false
  }
}

const changePage = (page) => {
  currentPage.value = page
  loadTasks()
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

onMounted(() => loadTasks())
</script>

<style scoped>
.rejected-list {
  padding: 24px;
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-color);
  margin-bottom: 24px;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: var(--white);
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  margin-right: 16px;
}

.stat-icon.rejected { background: linear-gradient(135deg, #fff2f0, #e57373); }
.stat-icon.total { background: linear-gradient(135deg, #f0f5ff, #adc6ff); }

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: var(--text-color);
  line-height: 1;
}

.stat-label {
  color: var(--text-secondary);
  margin-top: 4px;
  font-size: 14px;
}

.filter-bar {
  margin-bottom: 24px;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.filter-row {
  display: flex;
  align-items: center;
  gap: 24px;
  flex-wrap: wrap;
}

.filter-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-item label {
  color: var(--text-secondary);
  white-space: nowrap;
  font-size: 14px;
}

.filter-select {
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--white);
  font-size: 14px;
  min-width: 120px;
  transition: border-color 0.3s ease;
}

.filter-select:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(0, 122, 255, 0.1);
}

.search-item {
  flex: 1;
  min-width: 250px;
}

.search-box {
  display: flex;
  gap: 8px;
  align-items: center;
}

.search-input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-size: 14px;
  transition: border-color 0.3s ease;
}

.search-input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(0, 122, 255, 0.1);
}

.search-btn {
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 14px;
}

.task-list-card {
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 0;
  gap: 16px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 0;
  gap: 12px;
  text-align: center;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.empty h3 {
  color: var(--text-color);
  font-size: 18px;
  font-weight: 600;
  margin: 0;
}

.empty p {
  color: var(--text-secondary);
  font-size: 14px;
  margin: 0;
}

.tasks-table-container {
  overflow-x: auto;
}

.tasks-table {
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
  background-color: #f8f9fa;
  font-weight: 600;
  color: var(--text-secondary);
  font-size: 14px;
  position: sticky;
  top: 0;
  z-index: 1;
}

.task-row {
  transition: background-color 0.2s ease;
}

.task-row:hover {
  background-color: #f8f9fa;
}

.task-title {
  font-weight: 500;
  color: var(--text-color);
}

.task-title a {
  color: var(--primary-color);
  text-decoration: none;
  transition: color 0.3s ease;
}

.task-title a:hover {
  color: var(--primary-dark);
  text-decoration: underline;
}

.task-btn {
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 14px;
  text-decoration: none;
  display: inline-block;
  transition: all 0.3s ease;
}

.task-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 122, 255, 0.3);
}

.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 24px;
  padding: 20px;
  border-top: 1px solid var(--border-color);
  background-color: #f8f9fa;
}

.page-btn {
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 4px;
  transition: all 0.3s ease;
}

.page-btn:hover:not(:disabled) {
  background-color: var(--primary-light);
  transform: translateY(-2px);
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-icon {
  font-size: 12px;
}

.page-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  font-size: 14px;
  color: var(--text-secondary);
}

.total-count {
  font-size: 12px;
}

@media (max-width: 1200px) {
  .stats-cards {
    grid-template-columns: 1fr;
  }
  
  .filter-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .search-item {
    width: 100%;
  }
}

@media (max-width: 768px) {
  .rejected-list {
    padding: 16px;
  }
  
  .pagination {
    flex-direction: column;
    gap: 12px;
  }
  
  .page-info {
    order: -1;
  }
}
</style>
