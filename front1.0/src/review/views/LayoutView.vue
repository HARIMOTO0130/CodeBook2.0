<template>
  <div class="layout">
    <main class="main-content">
      <div class="content">
        <h1 class="page-title">{{ pageTitle }}</h1>
        <router-view />
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { authApi, taskApi } from '../api/review'

const router = useRouter()
const route = useRoute()

const user = ref(JSON.parse(localStorage.getItem('review_user') || '{}'))
const stats = ref({
  my_pending: 0
})

const pageTitle = computed(() => {
  const titles = {
    '/dashboard': '工作台',
    '/books': '教材列表',
    '/pending': '待审核',
    '/approved': '已通过',
    '/rejected': '已驳回',
    '/history': '审核历史',
    '/settings': '设置'
  }
  if (route.path.startsWith('/review/')) {
    return '审核详情'
  }
  if (route.path.startsWith('/books/')) {
    return '教材修改历史'
  }
  return titles[route.path] || '教材审核系统'
})

const loadStats = async () => {
  try {
    const data = await taskApi.getStats()
    stats.value = data
  } catch (err) {
    console.error('加载统计失败', err)
  }
}

const handleLogout = async () => {
  try {
    await authApi.logout()
  } catch (err) {
    console.error('退出失败', err)
  }
  localStorage.removeItem('review_token')
  localStorage.removeItem('review_user')
  router.push('/review/login')
}

onMounted(() => {
  loadStats()
})
</script>

<style scoped>
.layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.main-content {
  flex: 1;
  background: var(--bg-color);
}

.content {
  padding: 24px;
  overflow-y: auto;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 20px;
}
</style>
