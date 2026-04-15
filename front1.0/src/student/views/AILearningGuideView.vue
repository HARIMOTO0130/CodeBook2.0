<template>
  <div class="ai-learning-guide-container">
    <!-- 顶部面包屑 -->
    <div class="breadcrumb">
      <router-link to="/student/books" class="breadcrumb-item">书架</router-link>
      <span class="breadcrumb-separator">/</span>
      <router-link :to="`/student/books/${bookId}`" class="breadcrumb-item">{{ book?.title }}</router-link>
      <span class="breadcrumb-separator">/</span>
      <router-link :to="`/student/learn/${bookId}/${chapterId}`" class="breadcrumb-item">{{ currentSection?.title }}</router-link>
      <span class="breadcrumb-separator">/</span>
      <span class="breadcrumb-item current">AI 导学</span>
    </div>

    <!-- 主要内容区域 -->
    <div class="main-content">
      <div class="header-section">
        <h1>AI 导学 - {{ currentSection?.title }}</h1>
        <p class="section-description">{{ currentSection?.description || '本章内容' }}</p>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading" class="loading-container">
        <div class="loading-spinner"></div>
        <p>正在生成 AI 导学内容...</p>
      </div>

      <!-- 错误状态 -->
      <div v-else-if="error" class="error-container">
        <p class="error-message">{{ error }}</p>
        <button class="btn btn-primary" @click="loadGuideContent">重试</button>
      </div>

      <!-- 内容区域 -->
      <div v-else-if="guideContent" class="guide-content">
        <!-- 标签页导航 -->
        <div class="tab-navigation">
          <button 
            v-for="tab in tabs" 
            :key="tab.id"
            :class="['tab-button', { active: activeTab === tab.id }]"
            @click="activeTab = tab.id"
          >
            {{ tab.icon }} {{ tab.name }}
          </button>
        </div>

        <!-- 标签页内容 -->
        <div class="tab-content">
          <!-- 思维导图 -->
          <div v-if="activeTab === 'mindmap'" class="tab-pane">
            <div class="mindmap-container">
              <h3>章节思维导图</h3>
              <div v-if="guideContent.mindmap" class="mindmap-content">
                <div class="mindmap-visualization">
                  <div class="mindmap-tree">
                    <div class="mindmap-root">
                      <h4>{{ chapterTitle }}</h4>
                      <div class="mindmap-branches">
                        <div 
                          class="mindmap-branch" 
                          v-for="(branch, index) in mindmapBranches" 
                          :key="index"
                          :style="{ marginLeft: branch.indent * 10 + 'px' }"
                        >
                          <div class="branch-content">{{ branch.content }}</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                <div class="mindmap-text">
                  <pre>{{ guideContent.mindmap }}</pre>
                </div>
              </div>
              <div v-else class="empty-content">
                <p>暂无思维导图内容</p>
              </div>
            </div>
          </div>

          <!-- PPT -->
          <div v-if="activeTab === 'ppt'" class="tab-pane">
            <div class="ppt-container">
              <h3>章节 PPT</h3>
              <div v-if="guideContent.ppt" class="ppt-content">
                <div class="ppt-slides">
                  <div class="ppt-slide" v-for="(slide, index) in pptSlides" :key="index">
                    <div class="slide-header">
                      <h4>第 {{ index + 1 }} 页</h4>
                    </div>
                    <div class="slide-content">
                      <div v-html="slide"></div>
                    </div>
                  </div>
                </div>
              </div>
              <div v-else class="empty-content">
                <p>暂无 PPT 内容</p>
              </div>
            </div>
          </div>

          <!-- 关键概念对比 -->
          <div v-if="activeTab === 'concepts'" class="tab-pane">
            <div class="concepts-container">
              <h3>关键概念对比</h3>
              <div v-if="guideContent.key_concepts" class="concepts-content">
                <div v-for="(concept, index) in guideContent.key_concepts" :key="index" class="concept-card">
                  <div class="concept-header">
                    <h4>{{ concept.name }}</h4>
                  </div>
                  <div class="concept-body">
                    <p class="concept-description">{{ concept.description }}</p>
                    <div v-if="concept.comparison" class="concept-comparison">
                      <h5>对比分析</h5>
                      <p>{{ concept.comparison }}</p>
                    </div>
                  </div>
                </div>
              </div>
              <div v-else class="empty-content">
                <p>暂无关键概念对比内容</p>
              </div>
            </div>
          </div>

          <!-- 豆包重点笔记 -->
          <div v-if="activeTab === 'notes'" class="tab-pane">
            <div class="notes-container">
              <h3>豆包重点笔记</h3>
              <div v-if="guideContent.notes" class="notes-content">
                <div class="note-card">
                  <div class="note-header">
                    <h4>{{ chapterTitle }}</h4>
                  </div>
                  <div class="note-body">
                    <div v-html="formattedNotes"></div>
                  </div>
                </div>
              </div>
              <div v-else class="empty-content">
                <p>暂无重点笔记内容</p>
              </div>
            </div>
          </div>

          <!-- 章节总结 -->
          <div v-if="activeTab === 'summary'" class="tab-pane">
            <div class="summary-container">
              <h3>章节总结</h3>
              <div v-if="guideContent.summary" class="summary-content">
                <div class="summary-card">
                  <div class="summary-header">
                    <h4>{{ chapterTitle }}</h4>
                  </div>
                  <div class="summary-body">
                    <div v-html="formattedSummary"></div>
                  </div>
                </div>
              </div>
              <div v-else class="empty-content">
                <p>暂无章节总结内容</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 无内容状态 -->
      <div v-else class="empty-guide">
        <p>暂无 AI 导学内容</p>
        <button class="btn btn-primary" @click="generateGuideContent">生成 AI 导学内容</button>
      </div>
      
      <!-- 已有内容状态 - 显示重新生成按钮 -->
      <div v-if="guideContent" class="regenerate-guide">
        <button class="btn btn-secondary" @click="generateGuideContent">重新生成 AI 导学内容</button>
      </div>
    </div>

    <!-- 底部导航 -->
    <div class="bottom-nav">
      <router-link :to="`/student/books/${bookId}/chapters/${chapterId}`" class="btn">
        ← 返回学习页面
      </router-link>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '../api/api.js'

export default {
  name: 'AILearningGuideView',
  setup() {
    const route = useRoute()
    const router = useRouter()
    const bookId = computed(() => Number(route.params.bookId))
    const chapterId = computed(() => Number(route.params.chapterId))
    
    const book = ref(null)
    const currentSection = ref(null)
    const guideContent = ref(null)
    const loading = ref(false)
    const error = ref(null)
    
    const activeTab = ref('mindmap')
    const tabs = [
      { id: 'mindmap', name: '思维导图', icon: '🧠' },
      { id: 'ppt', name: 'PPT', icon: '📊' },
      { id: 'concepts', name: '关键概念对比', icon: '🔍' },
      { id: 'notes', name: '豆包重点笔记', icon: '📝' },
      { id: 'summary', name: '章节总结', icon: '📋' }
    ]

    // 加载书籍和章节信息
    const loadBookAndSection = async () => {
      try {
        book.value = await api.getBookDetail(bookId.value)
        
        // 检查书籍是否被锁定
        if (book.value.permission_status === 'locked') {
          console.log('🔒 书籍已被锁定，重定向到书籍大纲页面');
          router.push({ name: 'StudentBookOutline', params: { bookId: bookId.value } });
          return;
        }
        
        // 查找当前章节
        const sections = book.value?.chapters || []
        if (sections.length > 0) {
          if (sections[0] && Array.isArray(sections[0].sections)) {
            // 章节下有小节
            const allSections = []
            sections.forEach(ch => (ch.sections || []).forEach(sec => allSections.push(sec)))
            currentSection.value = allSections.find(s => s.id === chapterId.value) || allSections[0]
          } else {
            // 直接把章节当作节
            currentSection.value = sections.find(s => s.id === chapterId.value) || sections[0]
          }
        }
      } catch (err) {
        console.error('加载书籍和章节信息失败:', err)
        error.value = '加载书籍信息失败'
      }
    }

    // 加载 AI 导学内容
    const loadGuideContent = async () => {
      try {
        loading.value = true
        error.value = null
        
        // 检查章节是否存在
        if (!currentSection.value) {
          error.value = '章节不存在或已被删除'
          return
        }
        
        const response = await api.getAILearningGuide(bookId.value, chapterId.value)
        if (response) {
          guideContent.value = response
        } else {
          // 内容正在生成中，显示提示
          error.value = 'AI 导学内容正在生成中，请稍后刷新查看'
        }
      } catch (err) {
        console.error('加载 AI 导学内容失败:', err)
        // 提供更友好的错误提示
        if (err.message.includes('400')) {
          error.value = '章节不存在或已被删除'
        } else if (err.message.includes('404')) {
          error.value = '章节不存在或已被删除'
        } else {
          error.value = '加载 AI 导学内容失败'
        }
      } finally {
        loading.value = false
      }
    }

    // 生成 AI 导学内容
    const generateGuideContent = async () => {
      try {
        loading.value = true
        error.value = null
        
        // 检查章节是否存在
        if (!currentSection.value) {
          error.value = '章节不存在或已被删除'
          return
        }
        
        const response = await api.generateAILearningGuide(bookId.value, chapterId.value)
        console.log('生成AI导学内容响应:', response)
        // 生成后重新加载内容
        await loadGuideContent()
      } catch (err) {
        console.error('生成 AI 导学内容失败:', err)
        // 提供更友好的错误提示
        if (err.message.includes('400')) {
          error.value = '章节不存在或已被删除'
        } else if (err.message.includes('404')) {
          error.value = '章节不存在或已被删除'
        } else {
          error.value = '生成 AI 导学内容失败'
        }
      } finally {
        loading.value = false
      }
    }

    // 初始化
    onMounted(async () => {
      await loadBookAndSection()
      await loadGuideContent()
    })

    // 计算属性
    const chapterTitle = computed(() => {
      return currentSection.value?.title || '章节标题'
    })

    const mindmapBranches = computed(() => {
      if (!guideContent.value?.mindmap) return []
      const mindmap = guideContent.value.mindmap
      // 提取所有以 - 开头的行作为分支，包括不同层级的缩进
      const branches = mindmap.split('\n')
        .filter(line => line.trim().startsWith('- '))
        .map(line => {
          // 保留缩进以便在显示时体现层级关系
          const indent = line.match(/^\s*/)[0]
          const content = line.trim().replace(/^- /, '')
          return { content, indent: indent.length }
        })
      return branches
    })

    const pptSlides = computed(() => {
      if (!guideContent.value?.ppt) return []
      const ppt = guideContent.value.ppt
      // 按 ## 分割 PPT 页面
      const slides = ppt.split('## ')
        .filter(slide => slide.trim())
        .map(slide => {
          // 处理 Markdown 格式，转换为 HTML
          return slide
            .replace(/^# (.*)$/gm, '<h3>$1</h3>')
            .replace(/^### (.*)$/gm, '<h5>$1</h5>')
            .replace(/^- (.*)$/gm, '<li>$1</li>')
            .replace(/(<li>.*<\/li>)/gs, '<ul>$1</ul>')
            .replace(/\n/g, '<br>')
        })
      return slides
    })

    const formattedNotes = computed(() => {
      if (!guideContent.value?.notes) return ''
      const notes = guideContent.value.notes
      return notes
        .replace(/^# (.*)$/gm, '<h4>$1</h4>')
        .replace(/^## (.*)$/gm, '<h5>$1</h5>')
        .replace(/^### (.*)$/gm, '<h6>$1</h6>')
        .replace(/^- (.*)$/gm, '<li>$1</li>')
        .replace(/(<li>.*<\/li>)/gs, '<ul>$1</ul>')
        .replace(/\n/g, '<br>')
    })

    const formattedSummary = computed(() => {
      if (!guideContent.value?.summary) return ''
      const summary = guideContent.value.summary
      return summary
        .replace(/^# (.*)$/gm, '<h4>$1</h4>')
        .replace(/^## (.*)$/gm, '<h5>$1</h5>')
        .replace(/^### (.*)$/gm, '<h6>$1</h6>')
        .replace(/^- (.*)$/gm, '<li>$1</li>')
        .replace(/(<li>.*<\/li>)/gs, '<ul>$1</ul>')
        .replace(/\n/g, '<br>')
    })

    return {
      bookId,
      chapterId,
      book,
      currentSection,
      guideContent,
      loading,
      error,
      activeTab,
      tabs,
      loadGuideContent,
      generateGuideContent,
      chapterTitle,
      mindmapBranches,
      pptSlides,
      formattedNotes,
      formattedSummary
    }
  }
}
</script>

<style scoped>
.ai-learning-guide-container {
  min-height: 100vh;
  padding: 20px;
  background-color: #f5f5f5;
}

.breadcrumb {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  font-size: 14px;
}

.breadcrumb-item {
  margin-right: 10px;
  color: #333;
  text-decoration: none;
}

.breadcrumb-item.current {
  font-weight: bold;
  color: #007bff;
}

.breadcrumb-separator {
  margin-right: 10px;
  color: #999;
}

.main-content {
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.header-section {
  margin-bottom: 30px;
}

.header-section h1 {
  font-size: 24px;
  margin-bottom: 10px;
  color: #333;
}

.section-description {
  color: #666;
  line-height: 1.5;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #007bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-container {
  padding: 40px 20px;
  text-align: center;
}

.error-message {
  color: #dc3545;
  margin-bottom: 20px;
}

.tab-navigation {
  display: flex;
  border-bottom: 1px solid #dee2e6;
  margin-bottom: 20px;
}

.tab-button {
  padding: 10px 20px;
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  font-size: 16px;
  transition: all 0.3s ease;
}

.tab-button:hover {
  color: #007bff;
}

.tab-button.active {
  color: #007bff;
  border-bottom-color: #007bff;
  font-weight: bold;
}

.tab-content {
  min-height: 400px;
}

.tab-pane {
  padding: 20px 0;
}

.mindmap-container,
.ppt-container,
.concepts-container,
.notes-container,
.summary-container {
  margin-bottom: 30px;
}

.mindmap-container h3,
.ppt-container h3,
.concepts-container h3,
.notes-container h3,
.summary-container h3 {
  font-size: 18px;
  margin-bottom: 15px;
  color: #333;
}

/* 思维导图可视化 */
.mindmap-visualization {
  background-color: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
}

.mindmap-tree {
  display: flex;
  justify-content: center;
}

.mindmap-root {
  background-color: #007bff;
  color: white;
  padding: 15px 25px;
  border-radius: 8px;
  text-align: center;
  margin-bottom: 20px;
}

.mindmap-root h4 {
  margin: 0;
  font-size: 18px;
}

.mindmap-branches {
  margin-top: 20px;
}

.mindmap-branch {
  position: relative;
  margin-bottom: 10px;
  padding-left: 35px;
  transition: all 0.3s ease;
}

.mindmap-branch:hover {
  transform: translateX(8px);
}

.branch-content {
  background-color: #ffffff;
  border: 2px solid #4a90e2;
  border-radius: 8px;
  padding: 10px 15px;
  font-size: 14px;
  color: #333;
  display: inline-block;
  max-width: 350px;
  box-shadow: 0 3px 6px rgba(0, 0, 0, 0.1);
  position: relative;
  z-index: 1;
  transition: all 0.3s ease;
}

.branch-content:hover {
  background-color: #f0f7ff;
  box-shadow: 0 5px 12px rgba(0, 0, 0, 0.15);
  border-color: #357abd;
}

/* 为分支添加连接线 */
.mindmap-branch::before {
  content: '';
  position: absolute;
  left: 15px;
  top: 18px;
  width: 20px;
  height: 3px;
  background-color: #4a90e2;
  border-radius: 2px;
}

.mindmap-branch::after {
  content: '';
  position: absolute;
  left: 16px;
  top: 0;
  width: 3px;
  height: 100%;
  background-color: #4a90e2;
  border-radius: 2px;
}

/* 为最后一个分支添加特殊样式，避免垂直线过长 */
.mindmap-branch:last-child::after {
  height: 18px;
}

/* 为顶层分支添加特殊样式 */
.mindmap-branch:first-child::after {
  top: 18px;
}

/* 为不同层级的分支添加不同的背景色 */
.mindmap-branch:nth-child(1) .branch-content {
  background-color: #e7f3ff;
}

.mindmap-branch:nth-child(2) .branch-content {
  background-color: #e6f7ee;
}

.mindmap-branch:nth-child(3) .branch-content {
  background-color: #fff7e6;
}

.mindmap-branch:nth-child(4) .branch-content {
  background-color: #f3e7ff;
}

.mindmap-branch:nth-child(5) .branch-content {
  background-color: #fff0e6;
}

.mindmap-text {
  background-color: #f1f1f1;
  padding: 15px;
  border-radius: 4px;
  font-family: 'Courier New', Courier, monospace;
  white-space: pre-wrap;
  word-wrap: break-word;
  text-align: left;
  max-height: 200px;
  overflow-y: auto;
}

/* PPT展示 */
.ppt-slides {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.ppt-slide {
  background-color: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.ppt-slide:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.slide-header {
  background-color: #007bff;
  color: white;
  padding: 10px 15px;
  border-radius: 6px 6px 0 0;
  margin: -20px -20px 20px -20px;
}

.slide-header h4 {
  margin: 0;
  font-size: 16px;
}

.slide-content {
  line-height: 1.6;
  color: #333;
}

/* 概念对比 */
.concepts-content {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}

.concept-card {
  background-color: #ffffff;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  padding: 20px;
  flex: 1;
  min-width: 300px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.concept-card:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.concept-header {
  background-color: #28a745;
  color: white;
  padding: 10px 15px;
  border-radius: 6px 6px 0 0;
  margin: -20px -20px 20px -20px;
}

.concept-header h4 {
  margin: 0;
  font-size: 16px;
}

.concept-body {
  line-height: 1.6;
}

.concept-description {
  margin-bottom: 15px;
  color: #333;
}

.concept-comparison {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #dee2e6;
}

.concept-comparison h5 {
  margin-bottom: 10px;
  color: #333;
  font-size: 14px;
}

.concept-comparison p {
  color: #666;
  line-height: 1.5;
}

/* 笔记 */
.notes-content {
  display: flex;
  justify-content: center;
}

.note-card {
  background-color: #ffffff;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  padding: 20px;
  width: 100%;
  max-width: 900px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  margin: 0 auto;
}

.note-card:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.note-header {
  background-color: #ffc107;
  color: #333;
  padding: 10px 15px;
  border-radius: 6px 6px 0 0;
  margin: -20px -20px 20px -20px;
}

.note-header h4 {
  margin: 0;
  font-size: 16px;
}

.note-body {
  line-height: 1.6;
  color: #333;
}

.note-body h4 {
  font-size: 18px;
  margin-bottom: 15px;
  color: #333;
}

.note-body h5 {
  font-size: 16px;
  margin: 15px 0 10px 0;
  color: #555;
}

.note-body h6 {
  font-size: 14px;
  margin: 10px 0 5px 0;
  color: #666;
}

.note-body ul {
  margin: 10px 0;
  padding-left: 20px;
}

.note-body li {
  margin-bottom: 5px;
  color: #444;
}

.note-body br {
  margin-bottom: 10px;
}

/* 章节总结 */
.summary-content {
  display: flex;
  justify-content: center;
}

.summary-card {
  background-color: #ffffff;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  padding: 20px;
  width: 100%;
  max-width: 900px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  margin: 0 auto;
}

.summary-card:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.summary-header {
  background-color: #17a2b8;
  color: white;
  padding: 10px 15px;
  border-radius: 6px 6px 0 0;
  margin: -20px -20px 20px -20px;
}

.summary-header h4 {
  margin: 0;
  font-size: 16px;
}

.summary-body {
  line-height: 1.6;
  color: #333;
}

.summary-body h4 {
  font-size: 18px;
  margin-bottom: 15px;
  color: #333;
}

.summary-body h5 {
  font-size: 16px;
  margin: 15px 0 10px 0;
  color: #555;
}

.summary-body h6 {
  font-size: 14px;
  margin: 10px 0 5px 0;
  color: #666;
}

.summary-body ul {
  margin: 10px 0;
  padding-left: 20px;
}

.summary-body li {
  margin-bottom: 5px;
  color: #444;
}

.summary-body br {
  margin-bottom: 10px;
}

.empty-content {
  padding: 40px 20px;
  text-align: center;
  background-color: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  color: #666;
}

.empty-guide {
  padding: 60px 20px;
  text-align: center;
}

.empty-guide p {
  margin-bottom: 20px;
  color: #666;
}

.bottom-nav {
  margin-top: 30px;
  text-align: center;
}

.btn {
  display: inline-block;
  padding: 10px 20px;
  border: 1px solid #007bff;
  border-radius: 4px;
  background-color: #007bff;
  color: white;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn:hover {
  background-color: #0069d9;
  border-color: #0062cc;
}

.btn-primary {
  background-color: #007bff;
  border-color: #007bff;
}

@media (max-width: 768px) {
  .ai-learning-guide-container {
    padding: 10px;
  }

  .main-content {
    padding: 15px;
  }

  .tab-navigation {
    flex-wrap: wrap;
  }

  .tab-button {
    padding: 8px 12px;
    font-size: 14px;
  }
}
</style>