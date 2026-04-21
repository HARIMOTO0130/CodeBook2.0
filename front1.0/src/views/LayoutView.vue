<template>
  <div class="layout-container">
    <main class="main-content">
      <div class="main-body">
        <router-view />
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { authApi } from '../review/api/review.js'

const router = useRouter()
const user = ref(null)

const loadUserInfo = async () => {
  try {
    const res = await authApi.getProfile()
    user.value = res
  } catch (err) {
    console.error('加载用户信息失败:', err)
  }
}

const handleLogout = async () => {
  try {
    await authApi.logout()
  } catch (err) {
    console.error('退出登录失败:', err)
  } finally {
    localStorage.removeItem('review_token')
    localStorage.removeItem('token')
    localStorage.removeItem('userRole')
    router.push('/')
  }
}

onMounted(() => {
  loadUserInfo()
})
</script>

<style scoped>
.layout-container {
  display: flex;
  min-height: 100vh;
  background: var(--background-light);
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.main-body {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}
</style>
